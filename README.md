# cs2620-time
By Zijian (Carl) Ma and Alex Geng

Full Engineering Notebook: https://docs.google.com/document/d/1aPtVlrZ9ZlQ2iQyOhsGQcFSgXAOnO0vKZNSfnbas1h0/edit?usp=sharing
# Final Summary

<details>
<summary>1. Overview</summary>

In this simulation, three virtual machines (VM 0, VM 1, and VM 2) operate asynchronously. Each machine maintains its own logical clock that is incremented on internal events and updated on receiving messages. The logs record two timestamps for every event: the global time gotten from the system and the logical clock time. For receiving events, the log also notes the length of the message queue.

</details>

<details>
<summary>2. Logical Clock Jumps</summary>

### Internal Events:
Most internal events increment the logical clock by 1.
Example – VM 0’s log, the first two events are:
```
INTERNAL | ... | Logical Clock: 1
INTERNAL | ... | Logical Clock: 2
```

### Receive Events – Inducing Jumps:
- **Design Decision:** When a message is received, the logical clock is updated according to:
  ```
  New Clock = max(Local Clock, Received Clock) + 1
  ```
- This rule can cause jumps larger than 1 to maintain the causal ordering of events.
- The receiving machine must register the receipt as happening after the sender’s event.

### Broadcast Events (Event Value 3):
- When a broadcast occurs, the machine sends to both partners in one atomic event, increments its clock once, and logs a single combined send event.

</details>

<details>
<summary>3. Gaps and Patterns in Logical Clock Values</summary>

### Gaps as Macro-Level Patterns:
- **Jump Sizes:** The difference between consecutive logical clock values.
- **Overall Pattern:** Larger jumps (or gaps) occur when a machine receives a message from a faster machine, causing a significant catch-up jump.
- Example – A jump from **9 to 17** (a gap of 8) in VM 0’s log indicates the effect of receiving a message from a machine with a much faster clock.

### Drift Analysis:
- **Drift Between Machines:** Machines with higher tick rates tend to have logical clocks that advance more quickly.
- **Synchronization Effects:** When a slower machine receives a message from a faster machine, its logical clock jumps to catch up.

</details>

<details>
<summary>4. Message Queue Dynamics</summary>

### Queue Length Observations:
- The logs include the message queue length during receive events.
- **Example:**
  ```
  RECEIVE | System Time: ... | Logical Clock: 21 | From VM 2, Queue Length: 1
  ```

### Interpretation:
- Occasional non-zero queue lengths suggest that differences in processing speeds and network timings cause temporary message accumulation.
- Faster machines react more quickly and send updates with more current logical clock values.
- Slower machines that frequently receive a backlog of messages can lead to noticeable delays in reacting to events, a potential bottleneck.

</details>

<details>
<summary>5. Observations</summary>

### Extreme Drift and Message Overload Impact
#### A. The Effect of Reducing Internal Events
- Experiment: Lowering Internal Events (from 1-10 to 1-4)
- Machines relied almost entirely on receiving messages to advance their logical clock.
- **Key Insight:**
  - **VM1 became overwhelmed with messages from VM0**, preventing it from incrementing its own clock.
  - **VM1's logical clock remained in the 100s while VM0 was in the 200s**, an extreme divergence.

#### B. The Slow Machine’s Struggle (VM1)
- **VM1 had the highest logical clock drift compared to VM0:**
  - **Avg Drift: 119.43 | Max Drift: 238**
  - **VM1 was completely out of sync with VM0** because it was swamped by incoming messages.
- **VM2 Performed Better Than VM1:**
  - **Avg Drift: 4.93 | Max Drift: 15**
  - **Key Insight:** A small increase in processing speed made a **huge difference in drift**.

</details>

<details>
<summary>6. Design Considerations for Distributed Systems</summary>

The insights from such simulations help in understanding trade-offs:
- How to design protocols that mitigate the impact of uneven processing speeds.
- The importance of mechanisms (like logical clocks) that ensure consistency despite these differences.
- Approaches for load balancing and scaling, so that no single node becomes a performance bottleneck.

</details>

<details>
<summary>7. Unit Testing & Code Validation</summary>

To ensure correctness, **unit tests** were implemented in `test_simulation.py` for:
1. **Logical Clock Updates**
   - Verified that **internal events** incremented the clock correctly.
   - Checked that **message reception updated clocks based on Lamport's Rule**.
2. **Message Passing & Processing**
   - Ensured messages were **sent, queued, and retrieved correctly**.
3. **Logical Clock Drift Calculations**
   - Verified that drift between VMs was computed accurately.
4. **Logging & File Integrity**
   - Ensured log entries contained correct event information.

### **Key Insight from Testing:**
- Logical clock drift and message processing followed expected patterns, confirming that logical time discrepancies were caused by system design rather than implementation errors.

</details>

