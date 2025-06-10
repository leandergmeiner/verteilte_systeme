#!/bin/bash

log_file=log.txt
rm -f "$log_file"

# Start processes
poetry run python -u main.py nameserver >> "$log_file" 2>&1 &
name_server_pid=$!
echo "NameServer PID $name_server_pid"
sleep 0.05

poetry run python -u main.py dispatcher >> "$log_file" 2>&1 &
dispatcher_pid=$!
echo "Dispatcher PID $dispatcher_pid"
sleep 0.05

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    worker_address_prefix="[::]:5006"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    worker_address_prefix="localhost:5006"
fi
>>>>>>> Stashed changes
=======
worker_address_prefix="localhost:5006"  # Changed from [::]:5006 for macOS compatibility
worker_tasks=(sum hash reverse strlen floor softmax)
worker_pids=()

max_i=$((${#worker_tasks[@]} - 1))
for i in $(seq 0 $max_i); do
    task=${worker_tasks[i]}
    poetry run python -u main.py worker "$task" "$worker_address_prefix$i" >> "$log_file" 2>&1 &
    worker_pid=$!
    sleep 0.05
    echo "Task $task with PID $worker_pid"
    worker_pids+=("$worker_pid")
done

function client_test_task() {
    task=$1
    shift
    args=("$@")
    r=$(poetry run python main.py exec "$task" "${args[@]}")
    echo "Result for task $task with args ( $(printf "'%s' " "${args[@]}") ): $r"
}

# Client interaction
client_test_task sum 10 20 30
client_test_task hash "Hello World"
client_test_task reverse Hello World
client_test_task strlen Hello World
client_test_task floor 1.5 2.5 3.5
client_test_task softmax 1.2 0.6 0.2

# Clean Up
kill -9 "$name_server_pid" "$dispatcher_pid" "${worker_pids[@]}"
