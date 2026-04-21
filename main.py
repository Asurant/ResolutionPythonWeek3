from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum
import os
import json

app = FastAPI()

TASKS_FILE = "tasks.json"

#Note: Each task should look like this {"id": 1, "task": "Test Systems", "done": False, "eisenhower_matrix": Q2}

class EisenhowerVal(str, Enum):
    Q1 = "Q1"
    Q2 = "Q2"
    Q3 = "Q3"
    Q4 = "Q4"

class TaskBody(BaseModel):
    task: str
    done: bool = False
    eisenhower: EisenhowerVal

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r") as file:
        return json.load(file)
    
def save_tasks(tasks):
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=2)

@app.get("/tasks")
async def get_tasks(done: bool | None = None):
    tasks = load_tasks()

    if done == None:
        return tasks
    filter_tasks = []
    for task in tasks:
        if task["done"] == done:
            filter_tasks.append(task)
    return filter_tasks

@app.post("/tasks")
async def create_task(task: TaskBody):
    tasks = load_tasks()
    if len(tasks) == 0:
        new_id=1
    else:
        new_id = tasks[-1]["id"]+1
    tasks.append({"id": new_id, "task": task.task, "done": task.done, "eisenhower": task.eisenhower})
    save_tasks(tasks)
    return {"id": new_id, "task": task.task, "done": task.done, "eisenhower": task.eisenhower}

@app.patch("/tasks/{task_id}/complete")
async def complete_task(task_id: int):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            save_tasks(tasks)
            return tasks
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    tasks = load_tasks()
    new_tasks = []
    for task in tasks:
        if task["id"] != task_id:
            new_tasks.append(task)
    tasks = new_tasks
    save_tasks(new_tasks)
    return {"message": f"Task {task_id} deleted"}

@app.get("/tasks/stats")
async def get_stats():
    tasks = load_tasks()

    total = len(tasks)

    completed = 0
    for task in tasks:
        if task["done"]:
            completed+=1

    
    Q1completed = 0
    Q1total = 0
    for task in tasks:
        if task["eisenhower"] == "Q1":
            Q1total+=1
            if task["done"]:
                Q1completed+=1

    Q2completed = 0
    Q2total = 0
    for task in tasks:
        if task["eisenhower"] == "Q2":
            Q2total+=1
            if task["done"]:
                Q2completed+=1

    Q3completed = 0
    Q3total = 0
    for task in tasks:
        if task["eisenhower"] == "Q3":
            Q3total+=1
            if task["done"]:
                Q3completed+=1
    
    Q4completed = 0
    Q4total = 0
    for task in tasks:
        if task["eisenhower"] == "Q4":
            Q4total+=1
            if task["done"]:
                Q4completed+=1

    return{
        "total": total,
        "Q1total": Q1total,
        "Q2total": Q2total,
        "Q3total": Q3total,
        "Q4total": Q4total,
        "completed": completed,
        "Q1completed": Q1completed,
        "Q2completed": Q2completed,
        "Q3completed": Q3completed,
        "Q4completed": Q4completed,
        "remaining": total-completed,
        "Q1remaining": Q1total-Q1completed,
        "Q2remaining": Q2total-Q2completed,
        "Q3remaining": Q3total-Q3completed,
        "Q4remaining": Q4total-Q4completed,
    }