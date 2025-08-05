import sys
from pathlib import Path
from datetime import datetime

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from tools.sub_agent_architecture import CalculusAgent, Task, AgentType, TaskPriority


@pytest.mark.asyncio
async def test_derivative():
    agent = CalculusAgent("calc_test")
    task = Task(
        id="t1",
        type="derivative",
        description="Derivative of x**2",
        priority=TaskPriority.HIGH,
        agent_type=AgentType.CALCULUS,
        input_data={"expression": "x**2", "variable": "x"},
        created_at=datetime.now(),
    )
    result = await agent.execute_task(task)
    assert result.success
    assert result.output == "2*x"


@pytest.mark.asyncio
async def test_limit_one_over_zero():
    agent = CalculusAgent("calc_test")
    task = Task(
        id="t2",
        type="limit",
        description="Limit of 1/x as x->0",
        priority=TaskPriority.HIGH,
        agent_type=AgentType.CALCULUS,
        input_data={"expression": "1/x", "variable": "x", "point": 0},
        created_at=datetime.now(),
    )
    result = await agent.execute_task(task)
    assert result.success
    assert result.output in {"zoo", "oo"}
