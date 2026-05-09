from datetime import datetime

from airflow.decorators import dag
from airflow.operators.bash import BashOperator


@dag(
    dag_id="system_info",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["example", "bash"],
    access_control={
        "Admin": {"can_read", "can_edit", "can_delete"},
        "Op":    {"can_read", "can_edit", "can_dag_run"},
        "User":  {"can_read"},
        "Viewer": {"can_read"},
    },
)
def system_info():

    os_info = BashOperator(
        task_id="os_info",
        bash_command=(
            "echo '=== OS / Kernel ==='; "
            "uname -a; "
            "echo; "
            "echo '=== OS Release ==='; "
            "cat /etc/os-release 2>/dev/null || echo 'N/A'; "
        ),
    )

    cpu_info = BashOperator(
        task_id="cpu_info",
        bash_command=(
            "echo '=== CPU ==='; "
            "lscpu 2>/dev/null | grep -E 'Architecture|Model name|CPU\\(s\\)|Thread|Socket|MHz' "
            "|| grep -m1 'model name' /proc/cpuinfo || echo 'N/A'; "
        ),
    )

    memory_info = BashOperator(
        task_id="memory_info",
        bash_command=(
            "echo '=== Memory ==='; "
            "free -h; "
            "echo; "
            "echo '=== Disk ==='; "
            "df -h --output=source,size,used,avail,pcent,target 2>/dev/null || df -h; "
        ),
    )

    network_info = BashOperator(
        task_id="network_info",
        bash_command=(
            "echo '=== Hostname ==='; "
            "hostname; "
            "echo; "
            "echo '=== Network interfaces ==='; "
            "ip addr show 2>/dev/null || ifconfig 2>/dev/null || echo 'N/A'; "
            "echo; "
            "echo '=== DNS ==='; "
            "cat /etc/resolv.conf; "
        ),
    )

    [os_info, cpu_info, memory_info, network_info]


system_info()
