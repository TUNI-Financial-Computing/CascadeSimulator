// Last update: 2021-06-30
// inculde guard:
#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>        // For automatic conversion of STL containers
#include <vector>
#include <utility>               // For std::pair
// For the std::rotl function
#include <bit>
#include <cstdint>
#include <unordered_map>
#include <tuple>
#include <string>
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

namespace py = pybind11;

// Define a hash function for pairs

template<class A,class B>
struct std::hash<std::pair<A,B>>{
	size_t operator() (const pair<A,B>& p) const {
		return std::rotl(hash<A>{}(p.first),1) ^
			   hash<B>{}(p.second);
	}
};



struct Observation {
    std::unordered_map<std::string, py::object> data;  // Generic dictionary

    Observation() {
        data["symptom"] = py::int_(0);  // Default symptom value
    }

    void set_symptom(int value) {
        data["symptom"] = py::int_(value);
    }

    int get_symptom() const {
        return py::cast<int>(data.at("symptom"));
    }
};

struct parameters {
    std::unordered_map<int, std::unordered_map<int, double>> t_prob;
    std::vector<double> s_prob;
    std::vector<double> thresholds;
    std::unordered_map<int, std::unordered_map<int, double>> a_b;
    std::unordered_map<int, std::unordered_map<int,double>> delays;
    std::vector<double> decays;
};

using cascade = std::vector<std::tuple<int, double, Observation>>;

class CascadeGenerator {
    public:
        CascadeGenerator(const std::vector<std::vector<int>>& graph, parameters& params);
        ~CascadeGenerator();
        cascade get_cascade(const std::vector<int>& seed_set);
        std::vector<cascade> get_cascades(const std::vector<int>& seed_set, int num_cascades); 
    private:
        std::vector<std::vector<int>> _graph_adj;
        parameters _params;
        int _num_nodes;
        int _num_edges;
        bool _use_delay;
        bool _use_decay;
        bool _use_IC;
        bool _use_LT;
        bool _symptoms;
        std::unordered_map<std::pair<int,int>, int> _edge_index_map;
        std::unordered_map<int, std::pair<int,int>> _index_edge_map;
};