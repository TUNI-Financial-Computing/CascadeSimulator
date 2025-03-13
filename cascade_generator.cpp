#include <pybind11/pybind11.h>
#include <pybind11/stl.h>        // For automatic conversion of STL containers
#include <vector>
#include <utility>               // For std::pair
//#include <omp.h>
#include <list>
#include <iostream>
#include <algorithm>
#include <cmath>
#include <set>
// Include time measuring and precision setting
#include <chrono>
#include <iomanip>
// Library for random number generation
#include <random>
#include <stdexcept>
#include <queue>

#include "cascade_generator.h"

namespace py = pybind11;

CascadeGenerator::CascadeGenerator(const std::vector<std::vector<int>>& graph, parameters& params) {
    _graph_adj = graph;
    _params = params;
    _num_nodes = graph.size();
    // the number of edges is the total number of edges in the graph;
    // this is the sum of the number of edges in each node's adjacency list
    _num_edges = 0;
    for (int i = 0; i < _num_nodes; i++) {
        _num_edges += _graph_adj[i].size();
    }
    bool _use_delay = params.delays.size() > 0;
    if (_use_delay) {
        if (params.delays.size() != _num_nodes) {
            throw std::invalid_argument("The number of delays must be equal to the number of edges in the graph");
        }
    }
    bool _use_decay = params.decays.size() > 0;
    if (_use_decay) {
        if (params.decays.size() != _num_nodes) {
            throw std::invalid_argument("The number of decays must be equal to the number of nodes in the graph");
        }
    }
    bool _use_IC = params.t_prob.size() > 0;
    if (_use_IC) {
        if (params.t_prob.size() != _num_nodes) {
            throw std::invalid_argument("The number of transmission probabilities must be equal to the number of edges in the graph");
        }
    }
    _use_LT = params.thresholds.size() > 0;
    _symptoms = params.s_prob.size() > 0;
    if (!_use_IC && !_use_LT) {
        throw std::invalid_argument("At least one of the following parameters must be provided: t_prob, s_prob");
    }
}

CascadeGenerator::~CascadeGenerator() 
{
    // Destructor
}

using QueueEntry = std::tuple<int, double>;

// Custom comparator: makes priority queue a min-heap (smallest double first)
struct Compare {
    bool operator()(const QueueEntry& a, const QueueEntry& b) {
        return std::get<1>(a) > std::get<1>(b);  // Min-heap: smaller double has higher priority
    }
};


// Generate a single cascade
cascade CascadeGenerator::get_cascade(const std::vector<int>& seed_set) {
    // Function to generate a single cascade
    cascade c = {};
    std::priority_queue<QueueEntry, std::vector<QueueEntry>, Compare> q;    
    // Every seed vertex creates a default observation at time 0.0
    for (int i = 0; i < seed_set.size(); i++) {
        q.push(std::make_tuple(seed_set[i], 0.0));
        c.push_back(std::make_tuple(seed_set[i], 0.0, Observation()));
    }
    std::vector<bool> active(_num_nodes, false);
    std::vector<bool> finished(_num_nodes, false);
    std::vector<double> threshold_remaining = _params.thresholds;
    // Initialize the random number generator
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0.0, 1.0);
    // Initialize the time of the cascade
    double t = 0.0;
    // while the queue is not empty
    while (!q.empty())
    {
        auto [node, time] = q.top();
        q.pop();
        // if the node is already active, skip it
        if (finished[node]) {
            continue;
        }
        // mark the node as active
        active[node] = true;
        finished[node] = true;
        // Now go through the neighbours of the node
        for (int neighbour: _graph_adj.at(node))
        {
            // if the neighbour is already active, skip it
            if (active[neighbour]) {
                continue;
            }
            bool activated = false;
            // if the neighbour is not active, check if it gets activated
            double prob = dis(gen);
            if (_use_IC && prob < _params.t_prob[node][neighbour]) {
                activated = true;
            }
            if (_use_LT)
            {
                threshold_remaining[neighbour] -= _params.a_b[node][neighbour];
                if (threshold_remaining[neighbour] <= 0.0)
                {
                    activated = true;
                }
            }
            if (activated)
            {
                active[neighbour] = true;
                // if the neighbour gets activated, add it to the queue
                double delay = _use_delay?_params.delays[node][neighbour]:1.0;
                double activation_time = time + delay;
                q.push(std::make_tuple(neighbour, activation_time));
                // add the neighbour to the cascade
                Observation obs;
                obs.set_symptom(1);
                if (_symptoms) {
                    double symptom_prob = dis(gen);
                    if (symptom_prob > _params.s_prob[neighbour]) {
                        obs.set_symptom(0);
                    }
                } 
                c.push_back(std::make_tuple(neighbour, activation_time, obs));
            }
        }
    }
    return c;
}

// Generate multiple cascades
std::vector<cascade> CascadeGenerator::get_cascades(const std::vector<int>& seed_set, int num_cascades)
{
    // Function to generate multiple cascades
    std::vector<cascade> cascades(num_cascades);
    #pragma omp parallel for shared(cascades)
    for (int i = 0; i < num_cascades; i++) {
        cascades[i] = get_cascade(seed_set);
    }
    return cascades;
}
 

// Python module definition
PYBIND11_MODULE(cascade_generator, m) {
    py::class_<parameters>(m, "parameters")
        .def(py::init<>())
        .def_readwrite("t_prob", &parameters::t_prob)
        .def_readwrite("s_prob", &parameters::s_prob)
        .def_readwrite("thresholds", &parameters::thresholds)
        .def_readwrite("delays", &parameters::delays)
        .def_readwrite("decays", &parameters::decays);

    py::class_<CascadeGenerator>(m, "CascadeGenerator")
        .def(py::init<std::vector<std::vector<int>>&, parameters&>())
        .def("get_cascade", &CascadeGenerator::get_cascade)
        .def("get_cascades", &CascadeGenerator::get_cascades);
}
