#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <tuple>
#include <queue>
#include <stdexcept>
#include <string>
#include <random>

// Constants
namespace {
    constexpr double INITIAL_TIME = 0.0;
    constexpr double INITIAL_SYMPTOM = 0.0;
    constexpr double NO_SYMPTOM = 0.0;
    constexpr double HAS_SYMPTOM = 1.0;
    constexpr double NO_CUTOFF = -1.0;
    constexpr double DEFAULT_DELAY = 1.0;
    constexpr double UNIFORM_DIST_MIN = 0.0;
    constexpr double UNIFORM_DIST_MAX = 1.0;
}

std::string hello_from_bin() { return "Hello from CascadeSimulator"; }


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
    
    // Cutoff support
    double cutoff_time_;      // Cutoff time (-1.0 = no cutoff)
    bool use_cutoff_;         // Flag for fast check
    
    // Random number generation
    std::mt19937 rng_;        // Mersenne Twister RNG
    std::uniform_real_distribution<double> uniform_dist_;

    double get_delay(int i, int j)
    {
        // The delay is the time it takes for infection to spread from node i to node j;
        // This is a random variable, whose expectation is given by the edge delay
        const double expected_delay = edge_delays_[i][j];
        // The delay is exponential with expectation expected_delay:
        // The probability density function is f(x) = (1/expected_delay) * exp(-x/expected_delay)
        const double u = uniform_dist_(rng_);  // Uniform [0,1)
        const double delay = expected_delay * (-std::log(1.0 - u));

        return delay;
    }


public:
    // Constructor that takes a graph
    CascadeGenerator()
        : graph_({}), probability_(0), symptom_probability_(0), edge_probs_({}), node_symp_probs_({}), node_thresholds_({}), edge_effects_({}), edge_delays_({}), delayed_(false), symptomatic_(false), thresholded_(false), edge_probabilities_(false), n_nodes_(0), cutoff_time_(NO_CUTOFF), use_cutoff_(false), rng_(std::random_device{}()), uniform_dist_(UNIFORM_DIST_MIN, UNIFORM_DIST_MAX)
    {
        // void
    }

    void set_random_seed(int seed)
    {
        rng_.seed(seed);
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

    // Validate seed set
    void validate_seeds(const std::vector<int>& seed) const
    {
        if (seed.empty()) {
            throw std::invalid_argument("Seed set cannot be empty");
        }
        for (int node_id : seed) {
            if (node_id < 0 || node_id >= n_nodes_) {
                throw std::out_of_range("Seed node ID " + std::to_string(node_id) + 
                                       " is out of range [0, " + std::to_string(n_nodes_) + ")");
            }
        }
    }

    // Validate edge probabilities dimensions
    void validate_edge_probabilities() const
    {
        if (edge_probabilities_) {
            if (edge_probs_.size() != n_nodes_) {
                throw std::invalid_argument("Edge probabilities outer dimension (" + 
                    std::to_string(edge_probs_.size()) + ") must match number of nodes (" + 
                    std::to_string(n_nodes_) + ")");
            }
            for (int i = 0; i < n_nodes_; ++i) {
                if (edge_probs_[i].size() != graph_[i].size()) {
                    throw std::invalid_argument("Edge probabilities for node " + std::to_string(i) + 
                        " has " + std::to_string(edge_probs_[i].size()) + " entries but graph has " + 
                        std::to_string(graph_[i].size()) + " neighbors");
                }
            }
        }
    }

    // Validate node symptom probabilities
    void validate_symptom_probabilities() const
    {
        if (symptomatic_) {
            if (node_symp_probs_.size() != n_nodes_) {
                throw std::invalid_argument("Node symptom probabilities size (" + 
                    std::to_string(node_symp_probs_.size()) + ") must match number of nodes (" + 
                    std::to_string(n_nodes_) + ")");
            }
        }
    }

    // Validate edge delays dimensions
    void validate_edge_delays() const
    {
        if (delayed_) {
            if (edge_delays_.size() != n_nodes_) {
                throw std::invalid_argument("Edge delays outer dimension (" + 
                    std::to_string(edge_delays_.size()) + ") must match number of nodes (" + 
                    std::to_string(n_nodes_) + ")");
            }
            for (int i = 0; i < n_nodes_; ++i) {
                if (edge_delays_[i].size() != graph_[i].size()) {
                    throw std::invalid_argument("Edge delays for node " + std::to_string(i) + 
                        " has " + std::to_string(edge_delays_[i].size()) + " entries but graph has " + 
                        std::to_string(graph_[i].size()) + " neighbors");
                }
            }
        }
    }

    // Set cutoff time for cascade generation
    void set_cutoff(double cutoff_time)
    {
        if (cutoff_time >= INITIAL_TIME) {
            cutoff_time_ = cutoff_time;
            use_cutoff_ = true;
        } else {
            clear_cutoff();
        }
    }

    // Clear cutoff (disable time-based stopping)
    void clear_cutoff()
    {
        cutoff_time_ = NO_CUTOFF;
        use_cutoff_ = false;
    }

    std::vector<std::tuple<int, double, double>> generate_cascade_pq(const std::vector<int>& seed)
    {
        // Validate inputs
        validate_seeds(seed);
        validate_edge_probabilities();
        validate_symptom_probabilities();
        validate_edge_delays();
        
        std::vector<std::tuple<int, double, double>> cascade = {};
        // Make a priority queue of active nodes and initialize with the seed
        std::priority_queue<QNode, std::vector<QNode>, CompareByTime> active;
        std::vector<bool> infected(n_nodes_, false);
        std::vector<bool> is_active(n_nodes_, false);
        for (int node : seed) {
            active.push(QNode(node, INITIAL_TIME));
            infected[node] = true;
            is_active[node] = true;
        }

        // Include the seed in the cascade with 0 as symptom and time (node, time, symptom)
        // Only include seeds if they're within cutoff
        for (int node : seed) {
            if (!use_cutoff_ || INITIAL_TIME <= cutoff_time_) {
                cascade.push_back(std::make_tuple(node, INITIAL_TIME, INITIAL_SYMPTOM));
            }
        }
        while (!active.empty())
        {
            QNode qnode = active.top();
            active.pop();
            int node = qnode.node;
            double time = qnode.arrival_time;
            
            // CUTOFF: Early termination if time exceeds cutoff
            if (use_cutoff_ && time > cutoff_time_) {
                break;  // All remaining nodes in queue are beyond cutoff
            }
            
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
                double delay = time + (delayed_? get_delay(node, neighbor) : DEFAULT_DELAY);
                
                // CUTOFF: Skip neighbors that would arrive after cutoff
                if (use_cutoff_ && delay > cutoff_time_) {
                    continue;  // Don't add this neighbor to queue or cascade
                }
                
                if (uniform_dist_(rng_) > p)
                {
                    continue;
                }
                if (uniform_dist_(rng_) < q)
                {
                    cascade.push_back(std::make_tuple(neighbor, delay, HAS_SYMPTOM));
                }
                else
                {
                    cascade.push_back(std::make_tuple(neighbor, delay, NO_SYMPTOM));
                }
                active.push(QNode(neighbor, delay));
                infected[neighbor] = true;
                is_active[neighbor] = true;
            }
        }
        return cascade;
    }

    std::vector<std::tuple<int, double, double>> generate_cascade(const std::vector<int>& seed)
    {
        // Validate inputs
        validate_seeds(seed);
        validate_edge_probabilities();
        validate_symptom_probabilities();
        
        if (delayed_)
        {
            return generate_cascade_pq(seed);
        }
        std::vector<std::tuple<int, double, double>> cascade = {};
        // Make a priority queue of active nodes and initialize with the seed
        std::list<std::pair<int,double>> active;
        std::vector<bool> infected(n_nodes_, false);
        
        // Only include seeds if time 0 is within cutoff
        if (!use_cutoff_ || INITIAL_TIME <= cutoff_time_) {
            for (int node : seed) {
                active.push_back(std::make_pair(node, INITIAL_TIME));
                infected[node] = true;
            }
            // Include the seed in the cascade with 0 as symptom and time (node, time, symptom)
            for (int node : seed) {
                cascade.push_back(std::make_tuple(node, INITIAL_TIME, INITIAL_SYMPTOM));
            }
        }
        while (!active.empty())
        {
            std::pair<int,double> current = active.front();
            active.pop_front();
            int node = current.first;
            double time = current.second;
            
            // Early termination: if current time exceeds cutoff, stop processing
            if (use_cutoff_ && time > cutoff_time_) {
                break;
            }
            
            // For each neighbor of the node
            for (int j = 0; j < graph_[node].size(); ++j)
            {
                int neighbor = graph_[node][j];
                if (infected[neighbor])
                {
                    continue;
                }
                
                // Calculate next time (fixed 1.0 delay in non-delayed mode)
                double next_time = time + DEFAULT_DELAY;
                
                // Skip neighbors beyond cutoff
                if (use_cutoff_ && next_time > cutoff_time_) {
                    continue;
                }
                
                double p = edge_probabilities_? edge_probs_[node][j] : probability_;
                double q = symptomatic_? node_symp_probs_[neighbor] : symptom_probability_;
                if (uniform_dist_(rng_) > p)
                {
                    continue;
                }
                if (uniform_dist_(rng_) < q)
                {
                    cascade.push_back(std::make_tuple(neighbor, next_time, HAS_SYMPTOM));
                }
                else
                {
                    cascade.push_back(std::make_tuple(neighbor, next_time, NO_SYMPTOM));
                }
                active.push_back(std::make_pair(neighbor, next_time));
                infected[neighbor] = true;
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

PYBIND11_MODULE(cascade_generator_cpp, m) {
    py::class_<CascadeGenerator>(m, "CascadeGenerator")
        .def(py::init<>())
        .def("set_graph", &CascadeGenerator::set_graph)
        .def("set_probability", &CascadeGenerator::set_probability)
        .def("set_probabilities", &CascadeGenerator::set_probabilities)
        .def("set_symptom_probability", &CascadeGenerator::set_symptom_probability)
        .def("set_symptom_probabilities", &CascadeGenerator::set_symptom_probabilities)
        .def("set_delays", &CascadeGenerator::set_delays)
        .def("set_random_seed", &CascadeGenerator::set_random_seed, "Set random seed for reproducibility")
        .def("set_cutoff", &CascadeGenerator::set_cutoff, "Set time cutoff for cascade generation")
        .def("clear_cutoff", &CascadeGenerator::clear_cutoff, "Clear time cutoff")
        .def("generate_cascade", &CascadeGenerator::generate_cascade)
        .def("generate_cascades", &CascadeGenerator::generate_cascades);

    m.def("hello_from_bin", &hello_from_bin, R"pbdoc(
        A function that returns a Hello string.
        )pbdoc");
}
