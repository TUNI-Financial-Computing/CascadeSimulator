#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <tuple>
#include <queue>

// 1) Define a struct to hold (node, arrival_time)
struct QNode {
    int node;
    double arrival_time;

    // Optional: a constructor for convenience
    QNode(int n, double t) : node(n), arrival_time(t) {}
};

// 2) Define a custom comparator that orders by arrival_time
//    If you want the earliest (smallest) arrival_time on top, 
//    you compare '>' in the operator(), which effectively 
//    turns it into a min-heap.
struct CompareByTime {
    bool operator()(const QNode& a, const QNode& b) const {
        return a.arrival_time > b.arrival_time; 
    }
};




// Define the CascadeGenerator class
class CascadeGenerator {
private:
    std::vector<std::vector<int>> graph_;
    double probability_;
    double symptom_probability_;
    std::vector<std::vector<double>> edge_probs_; 
    std::vector<double> node_symp_probs_;
    std::vector<double> node_thresholds_;
    std::vector<std::vector<double>> edge_effects_;
    std::vector<std::vector<double>> edge_delays_;
    bool delayed_;
    bool symptomatic_;
    bool thresholded_;
    bool edge_probabilities_;
    int n_nodes_;

    double get_delay(int i, int j) 
    {
        assert(delayed_);
        // The delay is the time it takes for infection to spread from node i to node j;
        // This is a random variable, whose expecation is given by the edge delay
        double expected_delay = edge_delays_[i][j];
        // The delay is exponential with expectasion expected_delay:
        // The probability density function is f(x) = (1/expected_delay) * exp(-x/expected_delay)
        double delay =  expected_delay * (-std::log(1 - std::rand() / (RAND_MAX + 1.0)));

        return delay;
    }
    

public:
    // Constructor that takes a graph
    CascadeGenerator()
        : graph_({}), probability_(0), symptom_probability_(0), edge_probs_({}), node_symp_probs_({}), node_thresholds_({}), edge_effects_({}), edge_delays_({}), delayed_(false), symptomatic_(false), thresholded_(false), edge_probabilities_(false), n_nodes_(0) 
    {
        // void
    }
    
    void set_graph(const std::vector<std::vector<int>>& graph) 
    {
        graph_ = graph;
        n_nodes_ = graph.size();
    }

    // Set the base probability 
    void set_probability(double p) 
    {
        probability_ = p;
    }
    void set_probabilities(const std::vector<std::vector<double>>& edge_probs) 
    {
        edge_probs_ = edge_probs;
        edge_probabilities_ = true;
    }

    // Set the symptom probability (polymorphism as either int or vector)
    void set_symptom_probability(double q) 
    {
        symptom_probability_ = q;
    }
    void set_symptom_probabilities(const std::vector<double>& node_symp_probs) 
    {
        node_symp_probs_ = node_symp_probs;
        symptomatic_ = true;
    }

    void set_delays(const std::vector<std::vector<double>>& edge_delays) 
    {
        edge_delays_ = edge_delays;
        delayed_ = true;
    }

    std::vector<std::tuple<int, double, double>> generate_cascade(const std::vector<int>& seed) 
    {
        std::vector<std::tuple<int, double, double>> cascade = {};
        // Make a priority queue of active nodes and initialize with the seed
        std::priority_queue<QNode, std::vector<QNode>, CompareByTime> active;
        std::vector<bool> infected(n_nodes_, false);
        std::vector<bool> is_active(n_nodes_, false); 
        for (int node : seed) {
            active.push(QNode(node, 0.0));
            infected[node] = true;
            is_active[node] = true;
        }
        
        // Include the seed in the cascade with 0 as symptom and time (node, time, symptom)
        for (int node : seed) {
            cascade.push_back(std::make_tuple(node, 0.0, 0.0));
        }
        while (!active.empty())
        {
            QNode qnode = active.top();
            active.pop();
            int node = qnode.node;
            double time = qnode.arrival_time;
            if (!is_active[node]) {
                continue;
            }
            is_active[node] = false;
            // For each neighbor of the node
            for (int j = 0; j < graph_[node].size(); ++j) 
            {
                int neighbor = graph_[node][j];
                if (infected[neighbor]) 
                {
                    continue;
                }
                double p = edge_probabilities_? edge_probs_[node][j] : probability_;
                double q = symptomatic_? node_symp_probs_[neighbor] : symptom_probability_;
                double delay = time + (delayed_? get_delay(node, neighbor) : 1.0);
                if (std::rand() / (RAND_MAX + 1.0) > p)
                {
                    continue;
                }
                if (std::rand() / (RAND_MAX + 1.0) < q)
                {
                    cascade.push_back(std::make_tuple(neighbor, delay, 1.0));
                }
                else
                {
                    cascade.push_back(std::make_tuple(neighbor, delay, 0.0));
                }
                active.push(QNode(neighbor, delay));
                infected[neighbor] = true; 
                is_active[neighbor] = true;
            }
        }
        return cascade;
    }
    
    std::vector<std::vector<std::tuple<int,double,double>>> generate_cascades(const std::vector<int>& seed, int n_cascades) 
    {
        std::vector<std::vector<std::tuple<int,double,double>>> cascades(n_cascades);
        #pragma omp parallel for shared(cascades)
        for (int i = 0; i < n_cascades; ++i) 
        {
            auto cascade = generate_cascade(seed);
            cascades[i] = std::move(cascade);
        }
        return cascades;
    }
};

// Create the Python module named cascade_generator
namespace py = pybind11;

PYBIND11_MODULE(cascade_generator, m) {
    py::class_<CascadeGenerator>(m, "CascadeGenerator")
        .def(py::init<>())
        .def("set_graph", &CascadeGenerator::set_graph)
        .def("set_probability", &CascadeGenerator::set_probability)
        .def("set_probabilities", &CascadeGenerator::set_probabilities)
        .def("set_symptom_probability", &CascadeGenerator::set_symptom_probability)
        .def("set_symptom_probabilities", &CascadeGenerator::set_symptom_probabilities)
        .def("set_delays", &CascadeGenerator::set_delays)
        .def("generate_cascade", &CascadeGenerator::generate_cascade)
        .def("generate_cascades", &CascadeGenerator::generate_cascades)
        .def("set_symptom_probability", &CascadeGenerator::set_symptom_probability)
        .def("set_symptom_probabilities", &CascadeGenerator::set_symptom_probabilities);
}

