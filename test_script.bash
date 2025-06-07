#!/bin/bash

log_file=log.txt
rm $log_file

# Start processes
poetry run python -u main.py nameserver &>> $log_file &
name_server_pid=$!
echo NameServer PID $name_server_pid
sleep 0.05

poetry run python -u main.py dispatcher &>> $log_file &
dispatcher_pid=$!
echo Dispatcher PID $dispatcher_pid
sleep 0.05

worker_address_prefix="[::]:5006"
worker_tasks=(sum hash reverse strlen floor softmax)
worker_pids=()

max_i=$(echo "${#worker_tasks[@]} - 1" | bc)
for i in $(seq 0 $max_i); do
    task=${worker_tasks[i]}
    poetry run python -u main.py worker $task $worker_address_prefix$i &>> $log_file &
    worker_pid=$!
    sleep 0.05
    echo Task $task with PID $worker_pid
    worker_pids+=("$worker_pid")
done

function client_test_task() {
    task=$1
    all_args=("$@")
    args="${all_args[@]:1}"
    r=$(poetry run python main.py exec $task ${args[@]/#/})
    echo Result for task $task with args \( $(printf "'%s' " "${all_args[@]:1}")\): $r
}

# Client interaction
client_test_task sum 10 20 30
client_test_task hash "Hello World"
client_test_task reverse Hello World
client_test_task strlen Hello World
client_test_task floor 1.5 2.5 3.5
client_test_task softmax 1.2 0.6 0.2

# Clean Up
kill -9 $name_server_pid $dispatcher_pid ${worker_pids[@]/#/}