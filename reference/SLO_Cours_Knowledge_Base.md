---
name: slo-sustainable-logistics
description: Expert knowledge base for the EPFL/HEC Lausanne course "Sustainable Logistics Operations" (SLO, Spring 2026, Prof. Olivier Gallay). Use this skill IMMEDIATELY whenever the user asks about logistics optimization, supply chains, TSP, VRP, facility location, packing problems, heuristics, OR-Tools, sustainability in logistics, mobility/transport emissions, or any topic from this course. Trigger on keywords like: TSP, VRP, Clarke-Wright, bin packing, knapsack, facility location, supply chain, last mile, NP-hard, Google OR-Tools, mathematical programming, integer programming, subtour elimination, savings algorithm, scope 3 emissions, sustainable logistics, e-commerce logistics, city logistics. Also trigger for exam prep, quiz review, project help, or any assignment related to this course.
---

# Sustainable Logistics Operations (SLO) — Full Course Knowledge Base

**Course**: Sustainable Logistics Operations  
**Institution**: HEC Lausanne / E4S, MSc in Sustainable Management and Technology (SMT)  
**Semester**: Spring 2026  
**Professor**: Olivier Gallay  
**Tools**: Python, Google OR-Tools

---

## Chapter 0 — Course Overview

**Objectives:**
- Understand current mobility and logistics challenges
- Visualize supply chain components
- Build and solve mathematical optimization models for logistics
- Apply operations research methods (exact solvers + heuristics)
- Integrate sustainability/CO₂ impact into logistics decision-making

**Assessment:** Quiz (Week 9) + Group Project (presentation Week 14)

**Practical Sessions:** Python / Google OR-Tools  
PS1: OR-Tools intro | PS2: Assignment Problems | PS3: TSP | PS4: VRP | PS5: Packing | PS6: Facility Location

---

## Chapter 1 — Introduction: Mobility & Sustainability

**Why logistics matters:**
- Every product depends on logistics; mobility decisions shape cost, service, and climate.
- Transport = ~24% of global energy-related CO₂ emissions; road transport ≈ 75% of transport emissions; freight ≈ 40% of road CO₂.
- EU road transport CO₂ increased 21% (1990–2021); light commercial vehicles +49%.
- EU target: climate-neutral by 2050 (European Green Deal).
- Transport sector = 16.2% of global GHG (IEA 2022); 80% of corporate GHG is in supply chains (CDP 2023).

**Mobility post-COVID:** Temporary demand drop; accelerated e-commerce growth, which intensified last-mile pressure.

**Key tension:** Globalization + e-commerce → more logistics flows; sustainability regulation → pressure to reduce emissions. Optimization bridges this gap.

**Core message:** Every model in this course corresponds to a real daily decision (routing, warehouse placement, packing trucks). Those decisions directly affect emissions.

---

## Chapter 2 — Mathematical Programming

### Fundamentals

| Term | Definition |
|---|---|
| Decision variables | Factors under the control of the decision-maker |
| Parameters | Factors imposed by the environment (not controllable) |
| Constraints | Relationships among variables/parameters imposed by the problem |
| Objective function | Criterion to maximize or minimize |
| Feasible solution | All constraints are satisfied |
| Optimal solution | Feasible solution that optimizes the objective function |

### Classification of Models

**By variable type:**
- **Linear Program (LP):** Objective + all constraints are linear; variables are continuous (can be fractional).
- **Integer Program (IP):** Some/all variables must be integer.
  - *Pure IP*: all variables integer.
  - *Mixed IP (MIP)*: some integer, some continuous.

**By time horizon:**
- Static (single period) vs. Multistage (multiple periods)

**By uncertainty:**
- Deterministic (parameters are known) vs. Stochastic (parameters are random)

### Modeling Process (in practice)
1. Select planning horizon
2. Identify decision variables and parameters
3. Define constraints
4. Select objective function
5. Collect data
6. Solve with an appropriate algorithm
7. Sensitivity analysis

### Logistics Example (Urban Delivery)
- **Decision variables:** Price charged, number/type of vehicles, routes, hub locations
- **Objective:** Minimize CO₂ / cost / delay
- **Constraints:** Driver hours, vehicle capacity, time windows

---

## Chapter 3 — Supply Chains & Logistics

### Supply Chain Management (SCM)
- A supply chain = system of multiple actors linked by flows of **material, information, and money**, ultimately fulfilling a customer demand.
- Echelons: supply → production → shipment → distribution → (returns).
- SCM aims to maximize generated revenue = customer payment − total fulfillment cost.
- Only revenue source = the customer. Inter-actor money transfers are fund exchanges.
- SCM covers: outsourcing, procurement planning, supplier selection, location/capacity planning, logistics management, coordination, customer relations.

### Logistics Management (vs. SCM)
- Focuses on **specific parts** of the SC: efficient, effective forward and reverse **flow and storage of goods** from origin to consumption point.
- Detailed organization of operational processes for moving material goods.
- SCM = macro view; Logistics = operational/execution view.

### Key SCM Decisions
- Where and what to produce, how much
- Inventory quantities and locations
- Where to locate factories and distribution centers (→ Facility Location)

---

## Chapter 4 — Traveling Salesman Problem (TSP)

### Problem Definition
A salesman starts at home, visits **n customers exactly once**, and returns home — at **minimum cost** (distance, time, CO₂, etc.).

Formally: Find the shortest **Hamiltonian cycle** visiting n locations (starting and ending at location 0).

### Complexity
- TSP is **NP-hard**: no known polynomial-time algorithm for all instances.
- Belongs to combinatorial optimization (can be modeled as Integer Linear Program).
- Easy to describe, extremely hard to solve at scale.

### Formulation (Dantzig-Fulkerson-Johnson)
- **Decision variables:** x_ij ∈ {0,1} — 1 if route goes from i to j
- **Objective:** Minimize Σ c_ij · x_ij
- **Constraints:**
  1. Each location j entered exactly once: Σ_{i≠j} x_ij = 1
  2. Each location i exited exactly once: Σ_{j≠i} x_ij = 1
  3. **Subtour elimination** (DFJ): Σ_{i∈S, j∉S} x_ij ≥ 1 for all S⊆V, |S|≥2  
     (prevents disconnected sub-loops; exponential number of constraints → makes it hard)

### Solution Methods
- **Exact:** Branch-and-bound (used in OR-Tools for small n)
- **Heuristics:** Clarke & Wright savings algorithm, nearest neighbor, 2-opt, 3-opt

### Clarke & Wright Savings Algorithm (for TSP)
**Savings:** s_ij = c_i0 + c_0j − c_ij  
(how much we save by linking i→j instead of going i→depot→j)

**Algorithm:**
1. Start: each location visited separately from depot
2. Compute all savings s_ij
3. Sort savings descending
4. Merge routes greedily (checking feasibility)

---

## Chapter 5 — Vehicle Routing Problem (VRP) & Heuristics

### VRP Definition
Generalization of TSP with **multiple vehicles**:
- K identical vehicles, each with capacity Q, all based at depot (location 0)
- n customers, each with known demand q_i
- Must: assign vehicle to each customer + compute each vehicle's route
- Goal: minimize total cost (distance / CO₂ / time)

### VRP Formulation (graph-based)
- Graph G = (V, A) where V = {depot + n customers}, A = cost matrix c_ij
- Variables x_ijk = 1 if vehicle k travels from i to j
- Additional constraint: total demand on each route ≤ Q

### VRP Extensions
| Variant | Key constraint added |
|---|---|
| CVRP | Capacity constraint (basic VRP) |
| VRPTW | Time windows for each customer |
| Pickup & Delivery VRP | Items must be picked up before delivery |
| Split deliveries VRP | A customer can be served by multiple vehicles |
| Periodic VRP | Planning over multiple days |
| Heterogeneous fleet VRP | Different vehicle types |
| Dial-a-Ride (DARP) | Passenger transport with pickup/dropoff |
| Stochastic VRP | Uncertain demands or travel times |
| Dynamic VRP | Real-time changes to requests |

### Clarke & Wright Algorithm for VRP
Same savings formula: **s_ij = c_i0 + c_0j − c_ij**

**Merge rules:**
- (i) Two routes can merge if: both i and j are endpoints of their respective routes, AND merged route total demand ≤ Q
- (ii) If i and j are on the same route, do NOT merge (would create a subtour)

**Steps:** Initialize (one route per customer) → compute + sort savings → greedily merge feasible pairs → stop when no feasible merge exists.

### Heuristics Overview
- **Constructive heuristics:** Build a solution from scratch (e.g., nearest neighbor, savings algorithm)
- **Improvement heuristics:** Start from a solution and improve iteratively (e.g., 2-opt, 3-opt, Or-opt)
- **Metaheuristics:** Guided search avoiding local optima (e.g., simulated annealing, tabu search, genetic algorithms)

---

## Chapter 6 — Variants of the VRP

### VRPTW (VRP with Time Windows)
- Each customer i must be visited within [a_i, b_i]
- Vehicle can wait if it arrives early (at a_i)
- Infeasible if arrival > b_i

**Formulation:** Add time variables t_ij + big-M constraints to enforce time windows. Results in a Mixed Integer Linear Program (MILP).

**Key insight:** Time windows drastically reduce the feasible solution space, which can make the problem easier OR harder depending on tightness.

### Other Notable Variants
- **Multi-depot VRP:** Vehicles start from different depots
- **Open VRP:** Vehicles don't need to return to depot
- **Green VRP:** Minimize fuel/emissions explicitly (speed-dependent fuel consumption)
- **Electric VRP (E-VRP):** Include recharging stops; range constraints

---

## Chapter 7 — Evolutions in the Logistics Sector

### Mega-trends
1. **Continuous growth of logistics flows** (globalization, e-commerce)
2. **Increasing customer expectations** (speed, reliability, flexibility, low cost → same-day delivery)
3. **Rising competition** among logistics providers (pressure on profitability)
4. **Strong sustainability pressure** (scope 3 = ~90% of corporate CO₂; EU CSRD, CBAM)

### Mandatory Win-Win-Win
- Clients want: low price + high service quality
- Logistics providers need: profitability
- Governments want: societal gain (reduced emissions)
→ Optimization is the only way to satisfy all three simultaneously.

### City Logistics Challenges
- Fragmented demand in space and time
- Traffic jams at peak hours
- Space conflicts: delivery parking, urban access restrictions (e.g., low emission zones)

### Solutions
- **Last-mile innovations:** cargo bikes (−90% CO₂ vs. van for <5km, <25kg), light electric vehicles, delivery lockers
- **Urban consolidation centers:** shared last-mile from city edge; reduce vehicle entries by 40–70%
- **Crowd-shipping:** leverage public transport and bike-sharing networks
- **Autonomous delivery robots/drones:** low-speed, geofenced urban delivery
- **Same-day delivery:** only viable for dense urban areas with real-time inventory; often not profitable and always environmentally costly — requires careful feasibility analysis.

### Digital Transformation
- Real-time tracking and dynamic routing
- AI-based demand forecasting
- Digital twins of supply chains
- 3PL platforms and collaborative logistics

---

## Chapter 8 — Packing Problems

### Classification
| Problem | Objective |
|---|---|
| **Knapsack Problem** | Maximize value of items packed in ONE bin (not all items need to fit) |
| **Bin-Packing Problem** | Minimize number of bins needed to pack ALL items |

Both are **NP-hard** combinatorial optimization problems.

### 1D Bin-Packing Problem
- n items, each with weight w_i
- Unlimited bins, each with capacity W
- **Objective:** Pack all items using minimum number of bins

**Heuristics:**
- **First Fit (FF):** Place item in first bin where it fits
- **Best Fit (BF):** Place item in bin with least remaining space (tightest fit)
- **First Fit Decreasing (FFD):** Sort items descending by weight, then apply FF
- **Best Fit Decreasing (BFD):** Sort descending, then apply BF

### 2D and 3D Bin-Packing
- Items are rectangular; shape and positioning matter
- Constraints: boundaries not violated, items don't overlap, every item packed in one bin
- Much harder — spatial arrangement must be optimized

### Real-World Application
- **Truck loading:** maximize cargo utilization, minimize number of trucks needed
- **Container shipping:** 3D packing with weight/stability constraints
- **Palletization:** stacking constraints (fragile items on top, weight limits)

---

## Chapter 9 — Facility Location Problems (FLP)

### Problem Definition
Given:
- m customer locations (must all be served)
- n candidate facility locations
- Fixed cost c_j of opening facility at location j
- Transportation cost d_ij of serving customer i from facility j

**Goal:** Select which facilities to open AND assign each customer to one open facility, minimizing total fixed + transportation costs.

**Assumption:** Unlimited capacity → Uncapacitated Facility Location Problem (UFLP)

### Key Trade-off
- More facilities → lower transport costs but higher fixed costs
- Fewer facilities → higher transport costs but lower fixed costs
- **Optimal number and placement** balances both

### Formulation (MILP)
- **Binary variables:** y_j = 1 if facility j is opened; x_ij = 1 if customer i assigned to facility j
- **Objective:** Minimize Σ_j c_j·y_j + Σ_i Σ_j d_ij·x_ij
- **Constraints:**
  1. Each customer assigned to exactly one facility: Σ_j x_ij = 1 ∀i
  2. Customer can only be assigned to open facility: x_ij ≤ y_j ∀i,j
  3. Binarity: x_ij, y_j ∈ {0,1}

### Variants
- **Capacitated FLP (CFLP):** Facilities have limited capacity
- **p-Median Problem:** Open exactly p facilities, minimize total weighted distance
- **p-Center Problem:** Open exactly p facilities, minimize maximum distance to any customer
- **Hub Location:** Facilities are hubs in a network (e.g., airports, logistics hubs)

---

## Chapter 10 — Supply Chains & Sustainability

### Triple Bottom Line
Sustainability = balancing **Profit** (economic), **People** (social), and **Planet** (environmental).

### Climate & Supply Chains — Key Facts
- +1.1°C above pre-industrial levels (IPCC AR6, 2021)
- 16.2% of global GHG from transport (IEA 2022)
- 80% of corporate GHG is in supply chains (CDP 2023)
- $228B annual cost of extreme weather to supply chains (Swiss Re 2022)
- Road freight = 7% of global GHG; air freight = 100× more carbon-intensive than sea per tonne-km
- **Scope 3 emissions** (from supply chain) = 70–90% of corporate GHG footprint

### Sustainable Supply Chain Management (SSCM)
Definition (Seuring & Müller, 2008): Management of material, information and capital flows, AND cooperation with supply chain partners to achieve all **three triple bottom line goals simultaneously**.

**Strategic approaches:**
- Defensive/reactive: supplier management for risk and performance
- Proactive: supply chain management for sustainable products

**Four pillars (Carter & Rogers, 2008):** Strategy, Risk management, Organisational culture, Transparency

### Sustainability Incentives

| Type | Voluntary | Compulsory |
|---|---|---|
| External | GRI reporting, CDP disclosure, SBTi | EU CSRD, CBAM, EU Taxonomy, national carbon taxes |
| Internal | Net-zero pledges, circular design, green procurement | — |

### Key KPIs for Sustainable Logistics

**Environmental:** Carbon intensity (kg CO₂e/tonne-km), fleet electrification rate, empty run rate (target <20%), average load factor (target >80%), fuel efficiency, share of renewable energy, supplier GHG assessment coverage.

**Social/Economic:** Total sustainability investment, % suppliers with SBTi targets, Lost Time Injury (LTI) rate, % sustainable packaging, scope 3 categories 4 & 9 reduction.

**Framework:** Measure → Disclose → Target → Reduce → Verify (third-party assurance)

### Decarbonization Strategies
- **Modal shift:** road → rail or sea (much lower CO₂/tonne-km)
- **Fleet electrification:** especially for urban/short-haul
- **Load optimization:** maximize fill rates (direct application of VRP/packing optimization)
- **Route optimization:** minimize empty miles (direct application of TSP/VRP)
- **Last-mile innovation:** cargo bikes, delivery lockers, urban consolidation centers
- **Circular logistics / reverse logistics:** include returns in optimization models

---

## Practical Sessions — OR-Tools Implementation Guide

### OR-Tools Installation & Key Imports

```python
!pip install ortools

# CP-SAT solver (constraint satisfaction / integer programming)
from ortools.sat.python import cp_model

# Linear / MIP solver
from ortools.linear_solver import pywraplp

# Routing (TSP / VRP)
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# Knapsack
from ortools.algorithms.python import knapsack_solver
```

**Solver backends:**
- `'GLOP'` — LP (continuous variables only, fast)
- `'CLP'` — LP/MIP with CLP backend
- `'SCIP'` — MIP (integer variables, more general)
- `'CBC'` — MIP (open-source, good for TSP subtour elimination)
- `cp_model.CpModel()` / `cp_model.CpSolver()` — CP-SAT (constraint programming, very flexible)

---

### Session 1 — Introduction to OR-Tools: CP-SAT, LP, N-Queens

#### 1a. CP-SAT: Finding a Feasible Solution
```python
from ortools.sat.python import cp_model

model = cp_model.CpModel()

# Integer variables with domain [0, num_vals-1]
x = model.NewIntVar(0, num_vals - 1, 'x')
y = model.NewIntVar(0, num_vals - 1, 'y')
z = model.NewIntVar(0, num_vals - 1, 'z')

# Constraints
model.Add(x != y)
model.Add(x > z)

# Solve
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL:
    print(solver.Value(x), solver.Value(y), solver.Value(z))
```

#### 1b. LP Optimization with pywraplp (GLOP)
```python
from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver('GLOP')

# Continuous variables (non-negative)
x = solver.NumVar(0, solver.infinity(), 'x')
y = solver.NumVar(0, solver.infinity(), 'y')

# Constraints
solver.Add(x + 2 * y <= 14.0)
solver.Add(3 * x - y >= 0.0)
solver.Add(x - y <= 2.0)

# Objective
solver.Maximize(3 * x + 4 * y)

status = solver.Solve()
if status == pywraplp.Solver.OPTIMAL:
    print('Objective =', solver.Objective().Value())
    print('x =', x.solution_value(), 'y =', y.solution_value())
```

**Key OR-Tools LP concepts:**
- `solver.NumVar(lb, ub, name)` → continuous variable
- `solver.IntVar(lb, ub, name)` → integer variable
- `solver.Add(constraint)` → add constraint
- `solver.Maximize(expr)` / `solver.Minimize(expr)` → objective
- `solver.Solve()` → returns status (OPTIMAL, INFEASIBLE, etc.)
- `var.solution_value()` → get value after solving

#### 1c. N-Queens (CP-SAT with AllDifferent)
```python
model = cp_model.CpModel()
queens = [model.NewIntVar(0, board_size - 1, f'x{i}') for i in range(board_size)]

# All queens in different rows
model.AddAllDifferent(queens)

# No two queens on same diagonal
for i in range(board_size):
    diag1, diag2 = [], []
    for j in range(board_size):
        q1 = model.NewIntVar(0, 2 * board_size, f'diag1_{i}_{j}')
        diag1.append(q1)
        model.Add(q1 == queens[j] + j)
        q2 = model.NewIntVar(-board_size, board_size, f'diag2_{i}_{j}')
        diag2.append(q2)
        model.Add(q2 == queens[j] - j)
    model.AddAllDifferent(diag1)
    model.AddAllDifferent(diag2)

solver = cp_model.CpSolver()
status = solver.SearchForAllSolutions(model, solution_printer)
```

**Homework 1: Resource Allocation**
- Company produces products A (300 CHF, 240 units, 60 min) and B (240 CHF, 144 units, 60 min)
- 24,000 units components; 16 days × 8h production time
- Use GLOP; maximize profit

**Homework 2: Sudoku** — CP-SAT + `AddAllDifferent` on rows, columns, 3×3 blocks

**Homework 3: KenKen** — CP-SAT + cage constraints using `+`, `*`, `-`, `/` operations

---

### Session 2 — Assignment Problems

#### Assignment Problem (Worker–Task)
**Problem:** Assign n workers to m tasks (n > m), each worker to at most 1 task, each task to exactly 1 worker, minimize total cost.

```python
from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver('CLP')

costs = [[45,50,90,80], [40,70,55,70], [130,100,40,90], [45,80,120,50], [40,110,80,95]]
num_workers = len(costs)
num_tasks = len(costs[0])

# Binary variables: x[i,j] = 1 if worker i does task j
x = {}
for i in range(num_workers):
    for j in range(num_tasks):
        x[i, j] = solver.IntVar(0, 1, '')

# Each worker assigned to at most 1 task
for i in range(num_workers):
    solver.Add(solver.Sum([x[i, j] for j in range(num_tasks)]) <= 1)

# Each task assigned to exactly 1 worker
for j in range(num_tasks):
    solver.Add(solver.Sum([x[i, j] for i in range(num_workers)]) == 1)

# Minimize total cost
solver.Minimize(solver.Sum([costs[i][j] * x[i,j]
    for i in range(num_workers) for j in range(num_tasks)]))

status = solver.Solve()
if status == pywraplp.Solver.OPTIMAL:
    for i in range(num_workers):
        for j in range(num_tasks):
            if x[i, j].solution_value() > 0.5:
                print(f'Worker {i} → Task {j}, Cost = {costs[i][j]}')
```

#### Extended Assignment: Teams + Special Constraints
- Workers split into teams; each team handles at most `team_max` tasks
- Worker 0 must be assigned to task 2 or 3: `solver.Add(x[0,2] + x[0,3] == 1)`
- Team constraints: `solver.Add(solver.Sum([x[i,j] for i in team1 for j in range(num_tasks)]) <= team_max)`

#### Exercise: Sustainable Vehicle Assignment
- 10 vehicles (3 groups by autonomy range), 8 deliveries with known distances
- Group constraints: `sum(distance[j] * x[i,j] for i in group_k) <= max_autonomy_k`
- Minimize total environmental impact (CO₂ matrix)

#### Exercise: Bike Sharing Optimization
- 4 stations (A, B, C, D) with capacity, demand, current bikes
- Decision vars: `x[i,j]` = bikes moved from station i to j
- Constraints: capacity, demand satisfaction, truck capacity (≤ 10 bikes total)
- Visualize with `networkx` DiGraph

---

### Session 3 — Traveling Salesman Problem (TSP)

#### TSP: Iterative Subtour Elimination (LP/CBC approach)
The standard approach: solve the LP, detect subtours, add subtour elimination constraints, repeat until single tour.

```python
from ortools.linear_solver import pywraplp

def solve_model_eliminate(D, Subtours=[]):
    s = pywraplp.Solver.CreateSolver('CBC')
    n = len(D)
    # x[i][j] = 1 if route goes from i to j
    x = [[s.IntVar(0, 0 if D[i][j]==0 else 1, '') for j in range(n)] for i in range(n)]

    # Enter each node exactly once
    for j in range(n):
        s.Add(s.Sum(x[i][j] for i in range(n) if i!=j) == 1)
    # Leave each node exactly once
    for i in range(n):
        s.Add(s.Sum(x[i][j] for j in range(n) if i!=j) == 1)

    # Add subtour elimination constraints for known subtours
    for S in Subtours:
        s.Add(s.Sum(x[i][j] for i in S for j in S if i!=j) <= len(S)-1)

    s.Minimize(s.Sum(D[i][j]*x[i][j] for i in range(n) for j in range(n)))
    status = s.Solve()
    # ... extract tours from solution
    return status, s.Objective().Value(), tours

def solve_model(D):
    subtours, tours = [], []
    while len(tours) != 1:
        status, value, tours = solve_model_eliminate(D, subtours)
        if status == pywraplp.Solver.INFEASIBLE:
            break
        subtours = [t for t in tours if len(t) < len(D)]
    return status, value, tours[0]
```

**Swiss cities distance matrix example:**
Cities: Lausanne(0), Geneva(1), Zurich(2), Bern(3), Lugano(4), Luzern(5), Basel(6), St.Gallen(7), Chur(8)

#### TSP: OR-Tools Routing Library (recommended for larger instances)
```python
from ortools.constraint_solver import routing_enums_pb2, pywrapcp

def create_data_model():
    data = {}
    data['distance_matrix'] = [...]  # n×n matrix
    data['num_vehicles'] = 1
    data['depot'] = 0
    return data

def main():
    data = create_data_model()
    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']), data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)

    # Distance callback
    def distance_callback(from_idx, to_idx):
        from_node = manager.IndexToNode(from_idx)
        to_node = manager.IndexToNode(to_idx)
        return data['distance_matrix'][from_node][to_node]

    transit_cb_idx = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_cb_idx)

    # Search parameters
    search_params = routing_enums_pb2.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    solution = routing.SolveWithParameters(search_params)

    if solution:
        index = routing.Start(0)
        route = []
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        print('Route:', route)
        print('Total distance:', solution.ObjectiveValue())
```

**Complexity observation:** TSP solving time grows exponentially; exact methods fail around n=200 nodes in reasonable time.

**Homework: Colissimo Depot Location**
- 11 delivery locations; find optimal depot to minimize total TSP route
- Run TSP for each candidate depot; pick the one minimizing total distance

---

### Session 4 — Vehicle Routing Problem (VRP)

#### Basic VRP with OR-Tools Routing Library
```python
from ortools.constraint_solver import routing_enums_pb2, pywrapcp

def create_data_model():
    data = {}
    data['distance_matrix'] = [...]  # (n+1)×(n+1), index 0 = depot
    data['num_vehicles'] = 4
    data['depot'] = 0
    return data

def main():
    data = create_data_model()
    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']), data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_idx, to_idx):
        return data['distance_matrix'][manager.IndexToNode(from_idx)][manager.IndexToNode(to_idx)]

    transit_cb_idx = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_cb_idx)

    # Optional: add distance dimension to limit max route distance
    routing.AddDimension(transit_cb_idx, 0, 3000, True, 'Distance')
    dist_dimension = routing.GetDimensionOrDie('Distance')
    dist_dimension.SetGlobalSpanCostCoefficient(100)

    search_params = routing_enums_pb2.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    solution = routing.SolveWithParameters(search_params)
    # Print routes per vehicle...
```

#### CVRP: Capacitated VRP (adding demand/capacity constraint)
```python
def create_data_model():
    data = {}
    data['distance_matrix'] = [...]
    data['demands'] = [0, 1, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8]  # 0 for depot
    data['vehicle_capacities'] = [15, 15, 15, 15]
    data['num_vehicles'] = 4
    data['depot'] = 0
    return data

def main():
    data = create_data_model()
    manager = pywrapcp.RoutingIndexManager(...)
    routing = pywrapcp.RoutingModel(manager)

    # Distance callback (same as before)
    ...

    # Demand callback
    def demand_callback(from_idx):
        return data['demands'][manager.IndexToNode(from_idx)]

    demand_cb_idx = routing.RegisterUnaryTransitCallback(demand_callback)

    # Add capacity constraint
    routing.AddDimensionWithVehicleCapacity(
        demand_cb_idx, 0, data['vehicle_capacities'], True, 'Capacity')

    solution = routing.SolveWithParameters(search_params)
```

**Key VRP Routing API concepts:**
- `RoutingIndexManager(n_locations, n_vehicles, depot)` — manages node indexing
- `RoutingModel(manager)` — the routing model
- `RegisterTransitCallback(cb)` — register arc cost function
- `RegisterUnaryTransitCallback(cb)` — register node-level function (demand)
- `SetArcCostEvaluatorOfAllVehicles(cb_idx)` — set objective
- `AddDimension(cb, slack, capacity, fix_start, name)` — add a dimension (e.g. distance limit)
- `AddDimensionWithVehicleCapacity(cb, slack, capacities, fix_start, name)` — capacity per vehicle
- `FirstSolutionStrategy.PATH_CHEAPEST_ARC` — greedy construction heuristic

**Homework: Waste Collection Routes**
- Fleet of garbage trucks, depot + 10 collection points
- Each truck has max capacity; each district generates known daily waste
- Minimize total distance while respecting capacity

**Homework: Planzer EV Fleet Optimization**
- Replace 1 diesel truck (13 CHF/km) with 2 EVs (5 CHF/km), investment = 50,000 CHF
- Break-even analysis: `break_even_routes = 50000 / (cost_diesel - cost_ev)`
- Compare total route costs for both fleet configurations

---

### Session 5 — Packing Problems

#### Knapsack Problem (OR-Tools knapsack_solver)
```python
from ortools.algorithms.python import knapsack_solver

# Initialize solver
solver = knapsack_solver.KnapsackSolver(
    knapsack_solver.KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER,
    'KnapsackExample')

values = [360, 83, 59, 130, 431, 67, ...]  # value per item
weights = [[48, 30, 19, 36, 36, 48, ...]]  # list of weight dimensions
capacities = [850]  # capacity per dimension

solver.init(values, weights, capacities)
computed_value = solver.solve()

packed_items = [i for i in range(len(values)) if solver.best_solution_contains(i)]
print('Total value =', computed_value)
print('Packed items:', packed_items)
```

#### Multidimensional Knapsack (weight + volume)
```python
weights = [[48, 30, 19, ...],   # weight dimension
           [17, 10, 34, ...]]   # volume dimension
capacities = [850, 500]         # max weight, max volume
# Same API as above — solver handles multiple dimensions automatically
```

#### Multiple Knapsack (MIP formulation)
```python
from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver('SCIP')

data = {
    'weights': [48, 30, 42, 36, ...],
    'values':  [10, 30, 25, 50, ...],
    'bin_capacities': [100, 100, 100, 100, 100],
}

# x[i,b] = 1 if item i goes in bin b
x = {}
for i in data['all_items']:
    for b in data['all_knapsacks']:
        x[i, b] = solver.IntVar(0, 1, f'x_{i}_{b}')

# Each item in at most one bin
for i in data['all_items']:
    solver.Add(sum(x[i,b] for b in data['all_knapsacks']) <= 1)

# Capacity constraints
for b in data['all_knapsacks']:
    solver.Add(sum(x[i,b] * data['weights'][i] for i in data['all_items']) <= data['bin_capacities'][b])

# Maximize total value
solver.Maximize(sum(x[i,b] * data['values'][i]
    for i in data['all_items'] for b in data['all_knapsacks']))

solver.Solve()
```

#### Bin-Packing Problem (MIP formulation)
```python
from ortools.linear_solver import pywraplp

def create_data_model():
    data = {}
    data['weights'] = [48, 30, 19, 36, 36, 27, 42, 42, 36, 24, 30]
    data['items'] = list(range(len(data['weights'])))
    data['bins'] = data['items']  # enough bins = worst case 1 item per bin
    data['bin_capacity'] = 100
    return data

solver = pywraplp.Solver.CreateSolver('SCIP')

# x[i,j] = 1 if item i is in bin j
x = {(i,j): solver.IntVar(0, 1, '') for i in data['items'] for j in data['bins']}
# y[j] = 1 if bin j is used
y = {j: solver.IntVar(0, 1, '') for j in data['bins']}

# Each item in exactly one bin
for i in data['items']:
    solver.Add(sum(x[i,j] for j in data['bins']) == 1)

# Bin capacity
for j in data['bins']:
    solver.Add(sum(x[i,j] * data['weights'][i] for i in data['items'])
               <= y[j] * data['bin_capacity'])

# Minimize number of bins
solver.Minimize(sum(y[j] for j in data['bins']))

solver.Solve()
```

**Homework: Crop Planning Optimization**
- 5 crops (wheat, corn, rice, potato, carrot) with profit, water, nutrient requirements
- Limited land, water, nutrient budget
- Maximize total profit → LP/IP with resource constraints

---

### Session 6 — Facility Location Problems

#### P-Median Problem (CP-SAT)
**Goal:** Open exactly p facilities to minimize total weighted distance (demand × distance).

```python
from ortools.sat.python import cp_model as cp

model = cp.CpModel()

p = 3                  # number of facilities to open
num_customers = 6
num_warehouses = 4
demand = [100, 80, 80, 70, 20, 50]

# Distance matrix: distance[customer][warehouse]
distance = [[...]]

# y[j] = 1 if warehouse j is opened
y = [model.NewBoolVar(f'y_{j}') for j in range(num_warehouses)]

# x[i][j] = 1 if customer i assigned to warehouse j
x = [[model.NewBoolVar(f'x_{i}_{j}') for j in range(num_warehouses)]
     for i in range(num_customers)]

# Open exactly p warehouses
model.Add(sum(y) == p)

# Each customer assigned to exactly one warehouse
for i in range(num_customers):
    model.Add(sum(x[i]) == 1)

# Customer can only be assigned to open warehouse
for i in range(num_customers):
    for j in range(num_warehouses):
        model.Add(x[i][j] <= y[j])

# Minimize weighted total distance
model.Minimize(sum(demand[i] * distance[i][j] * x[i][j]
    for i in range(num_customers) for j in range(num_warehouses)))

solver = cp.CpSolver()
solver.Solve(model)
```

#### Set-Covering Problem (CP-SAT)
**Goal:** Open minimum number of facilities such that every customer is within a given distance threshold.

```python
model = cp.CpModel()

min_distance = 120       # coverage radius
num_cities = 9
# Cities: 0:Lausanne 1:Geneva 2:Zurich 3:Bern 4:Lugano 5:Luzern 6:Basel 7:St.Gallen 8:Chur

distance = [[...]]  # 9×9 Swiss city distance matrix

# y[j] = 1 if city j has a warehouse
y = [model.NewBoolVar(f'y_{j}') for j in range(num_cities)]

# Each city must be covered by at least one open warehouse within min_distance
for i in range(num_cities):
    model.Add(sum(y[j] for j in range(num_cities)
                  if distance[i][j] <= min_distance) >= 1)

# Minimize number of open warehouses
model.Minimize(sum(y))

solver = cp.CpSolver()
solver.Solve(model)
print('Warehouses opened:', [j for j in range(num_cities) if solver.Value(y[j])])
```

**Homework: Facility Opening with Environmental Impact**
- Candidate factory locations with fixed cost, capacity, environmental impact
- Customers with known demand and transportation costs
- Minimize total cost (fixed + transport) while meeting demand and staying within impact budget

```python
from ortools.linear_solver import pywraplp

# x[i,j] = 1 if customer j served by facility i
# y[i] = 1 if facility i is opened
solver = pywraplp.Solver.CreateSolver('SCIP')
x = {(i,j): solver.IntVar(0,1,'') for i in range(n_facilities) for j in range(n_customers)}
y = {i: solver.IntVar(0,1,'') for i in range(n_facilities)}

# Customer demand satisfaction
for j in range(n_customers):
    solver.Add(sum(x[i,j] for i in range(n_facilities)) == 1)

# Capacity constraints
for i in range(n_facilities):
    solver.Add(sum(demand[j]*x[i,j] for j in range(n_customers)) <= capacity[i]*y[i])

# Environmental impact budget
solver.Add(sum(impact[i]*y[i] for i in range(n_facilities)) <= max_impact)

# Minimize total cost
solver.Minimize(sum(opening_cost[i]*y[i] for i in range(n_facilities)) +
                sum(transport_cost[i][j]*x[i,j] for i,j in x))
```

---

## Common OR-Tools Patterns & Tips

### Variable Types
| Type | API | Use when |
|---|---|---|
| Continuous | `solver.NumVar(lb, ub, name)` | LP, relaxed MIP |
| Integer (MIP) | `solver.IntVar(lb, ub, name)` | MIP with pywraplp |
| Boolean (CP) | `model.NewBoolVar(name)` | Binary decisions in CP-SAT |
| Integer (CP) | `model.NewIntVar(lb, ub, name)` | General integer in CP-SAT |

### Solver Selection Guide
| Problem type | Recommended solver |
|---|---|
| Pure LP | `'GLOP'` |
| Assignment / MIP | `'SCIP'` or `'CLP'` |
| TSP (exact, small) | `'CBC'` with subtour elimination |
| TSP / VRP (large) | `pywrapcp.RoutingModel` |
| Knapsack | `knapsack_solver` |
| Bin-packing | `'SCIP'` with MIP formulation |
| Facility Location | `cp_model.CpModel` or `'SCIP'` |
| N-Queens / Sudoku | `cp_model.CpModel` |

### Printing Solutions
```python
# pywraplp
if status == pywraplp.Solver.OPTIMAL:
    print('Objective =', solver.Objective().Value())
    print('Time =', solver.WallTime(), 'ms')

# CP-SAT
if status == cp_model.OPTIMAL:
    print('Objective =', solver.ObjectiveValue())

# Routing
if solution:
    print('Total distance =', solution.ObjectiveValue())
```

### Visualisation Tools Used in Sessions
```python
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx  # for flow/assignment visualization
```

---

| Concept | Formula / Key Idea |
|---|---|
| Clarke-Wright Saving | s_ij = c_i0 + c_0j − c_ij |
| TSP complexity | NP-hard; 2^n − 1 subtour elimination constraints |
| VRP vs TSP | VRP = TSP + multiple vehicles + capacity constraints |
| Bin-packing complexity | NP-hard; FFD gives good approximate solutions |
| FLP objective | min Σ c_j·y_j + Σ d_ij·x_ij |
| Scope 3 emissions | 70–90% of corporate GHG → supply chain is key lever |
| Last-mile cost share | 28% of total delivery cost; 25% of urban freight GHG |

---

## Tools & Implementation

- **Google OR-Tools:** Main solver used in practical sessions (Python API)
  - Supports VRP, TSP, bin packing, assignment problems
  - Uses CP-SAT solver for integer programs
- **Python:** All practical sessions use Python
- **Mathematical modeling:** Always formulate as MIP/LP before coding

---

*Course: SLO — Sustainable Logistics Operations, HEC Lausanne / EPFL E4S, Spring 2026*
