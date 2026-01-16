#!/usr/bin/env python3
"""
一个功能完整的待办事项管理系统
支持任务的增删改查、分类管理、优先级设置和数据持久化
"""

import json
import os
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Optional


class TaskStatus(Enum):
    """任务状态枚举"""
    TODO = "待办"
    IN_PROGRESS = "进行中"
    DONE = "已完成"
    CANCELLED = "已取消"


class PriorityLevel(Enum):
    """任务优先级枚举"""
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"
    URGENT = "紧急"


class Task:
    """任务类"""
    def __init__(
        self,
        title: str,
        description: str = "",
        category: str = "默认分类",
        priority: PriorityLevel = PriorityLevel.MEDIUM,
        due_date: Optional[datetime] = None,
        task_id: Optional[int] = None
    ):
        self.task_id = task_id or self._generate_id()
        self.title = title
        self.description = description
        self.category = category
        self.priority = priority
        self.status = TaskStatus.TODO
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.due_date = due_date
        self.completed_at: Optional[datetime] = None

    def _generate_id(self) -> int:
        """生成唯一任务ID"""
        return int(datetime.now().timestamp() * 1000000)

    def mark_as_done(self) -> None:
        """标记任务为已完成"""
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()

    def mark_as_in_progress(self) -> None:
        """标记任务为进行中"""
        self.status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.now()

    def mark_as_cancelled(self) -> None:
        """标记任务为已取消"""
        self.status = TaskStatus.CANCELLED
        self.updated_at = datetime.now()

    def update(self, **kwargs) -> None:
        """更新任务信息"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()

    def is_overdue(self) -> bool:
        """检查任务是否逾期"""
        if self.due_date and self.status != TaskStatus.DONE:
            return datetime.now() > self.due_date
        return False

    def to_dict(self) -> Dict:
        """转换为字典用于序列化"""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Task":
        """从字典创建任务对象"""
        task = cls(
            title=data["title"],
            description=data.get("description", ""),
            category=data.get("category", "默认分类"),
            priority=PriorityLevel(data.get("priority", "中")),
            task_id=data["task_id"]
        )
        task.status = TaskStatus(data.get("status", "待办"))
        task.created_at = datetime.fromisoformat(data["created_at"])
        task.updated_at = datetime.fromisoformat(data["updated_at"])
        task.due_date = datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None
        task.completed_at = datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None
        return task

    def __str__(self) -> str:
        """字符串表示"""
        due_date_str = f"截止日期: {self.due_date.strftime('%Y-%m-%d %H:%M')}" if self.due_date else "无截止日期"
        overdue_str = " (逾期)" if self.is_overdue() else ""
        return (
            f"ID: {self.task_id}\n"
            f"标题: {self.title}\n"
            f"描述: {self.description}\n"
            f"分类: {self.category}\n"
            f"优先级: {self.priority.value}\n"
            f"状态: {self.status.value}{overdue_str}\n"
            f"{due_date_str}\n"
            f"创建时间: {self.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"更新时间: {self.updated_at.strftime('%Y-%m-%d %H:%M')}"
        )


class TaskManager:
    """任务管理器类"""
    def __init__(self, data_file: str = "tasks.json"):
        self.data_file = data_file
        self.tasks: List[Task] = []
        self.load_tasks()

    def load_tasks(self) -> None:
        """从文件加载任务"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    tasks_data = json.load(f)
                    self.tasks = [Task.from_dict(data) for data in tasks_data]
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载任务失败: {e}")
                self.tasks = []
        else:
            self.tasks = []

    def save_tasks(self) -> None:
        """保存任务到文件"""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump([task.to_dict() for task in self.tasks], f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"保存任务失败: {e}")

    def add_task(self, task: Task) -> None:
        """添加任务"""
        self.tasks.append(task)
        self.save_tasks()
        print("任务添加成功！")

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """根据ID获取任务"""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def delete_task(self, task_id: int) -> bool:
        """删除任务"""
        task = self.get_task_by_id(task_id)
        if task:
            self.tasks.remove(task)
            self.save_tasks()
            print("任务删除成功！")
            return True
        print("未找到该任务！")
        return False

    def list_tasks(self, filter_status: Optional[TaskStatus] = None, filter_category: Optional[str] = None) -> List[Task]:
        """列出任务，可以按状态或分类过滤"""
        filtered_tasks = self.tasks
        if filter_status:
            filtered_tasks = [task for task in filtered_tasks if task.status == filter_status]
        if filter_category:
            filtered_tasks = [task for task in filtered_tasks if task.category == filter_category]
        return sorted(filtered_tasks, key=lambda x: x.created_at, reverse=True)

    def get_categories(self) -> List[str]:
        """获取所有分类"""
        categories = set(task.category for task in self.tasks)
        return sorted(list(categories))

    def get_statistics(self) -> Dict:
        """获取任务统计信息"""
        total = len(self.tasks)
        done = sum(1 for task in self.tasks if task.status == TaskStatus.DONE)
        in_progress = sum(1 for task in self.tasks if task.status == TaskStatus.IN_PROGRESS)
        todo = sum(1 for task in self.tasks if task.status == TaskStatus.TODO)
        cancelled = sum(1 for task in self.tasks if task.status == TaskStatus.CANCELLED)
        overdue = sum(1 for task in self.tasks if task.is_overdue())
        
        return {
            "total": total,
            "done": done,
            "in_progress": in_progress,
            "todo": todo,
            "cancelled": cancelled,
            "overdue": overdue,
            "completion_rate": (done / total * 100) if total > 0 else 0
        }


class TaskManagerUI:
    """任务管理器用户界面"""
    def __init__(self):
        self.manager = TaskManager()

    def display_menu(self) -> None:
        """显示主菜单"""
        print("\n" + "="*50)
        print("📋 待办事项管理系统")
        print("="*50)
        print("1. 添加新任务")
        print("2. 查看所有任务")
        print("3. 按状态筛选任务")
        print("4. 按分类筛选任务")
        print("5. 更新任务")
        print("6. 标记任务为完成")
        print("7. 删除任务")
        print("8. 查看统计信息")
        print("9. 退出系统")
        print("="*50)

    def get_valid_input(self, prompt: str, input_type: type = str, valid_options: Optional[List] = None) -> any:
        """获取有效输入"""
        while True:
            try:
                user_input = input(prompt).strip()
                if not user_input:
                    print("输入不能为空，请重新输入！")
                    continue
                
                if input_type == int:
                    value = int(user_input)
                else:
                    value = user_input
                
                if valid_options and value not in valid_options:
                    print(f"输入无效，请从以下选项中选择: {valid_options}")
                    continue
                
                return value
            except ValueError:
                print(f"输入无效，请输入{input_type.__name__}类型的值！")

    def add_task_ui(self) -> None:
        """添加任务界面"""
        print("\n➕ 添加新任务")
        title = self.get_valid_input("请输入任务标题: ")
        description = input("请输入任务描述 (可选): ").strip()
        category = input("请输入任务分类 (可选，默认: 默认分类): ").strip() or "默认分类"
        
        priority_options = [level.value for level in PriorityLevel]
        priority_input = self.get_valid_input(
            f"请输入优先级 ({'/'.join(priority_options)}，默认: 中): ",
            valid_options=priority_options + [""]
        ) or "中"
        priority = PriorityLevel(priority_input)
        
        due_date_input = input("请输入截止日期 (YYYY-MM-DD HH:MM，可选): ").strip()
        due_date = None
        if due_date_input:
            try:
                due_date = datetime.strptime(due_date_input, "%Y-%m-%d %H:%M")
            except ValueError:
                print("日期格式无效，将不设置截止日期")
        
        task = Task(
            title=title,
            description=description,
            category=category,
            priority=priority,
            due_date=due_date
        )
        self.manager.add_task(task)
        print(f"\n📝 任务已创建:")
        print(task)

    def list_tasks_ui(self, tasks: List[Task]) -> None:
        """列出任务界面"""
        if not tasks:
            print("\n📭 暂无任务")
            return
        
        print(f"\n📋 共找到 {len(tasks)} 个任务:")
        for i, task in enumerate(tasks, 1):
            print(f"\n--- 任务 {i} ---")
            print(task)

    def update_task_ui(self) -> None:
        """更新任务界面"""
        print("\n✏️ 更新任务")
        task_id = self.get_valid_input("请输入要更新的任务ID: ", int)
        task = self.manager.get_task_by_id(task_id)
        
        if not task:
            print("未找到该任务！")
            return
        
        print("\n当前任务信息:")
        print(task)
        
        print("\n请输入新的任务信息 (按回车跳过不更新):")
        title = input(f"新标题 ({task.title}): ").strip() or task.title
        description = input(f"新描述 ({task.description}): ").strip() or task.description
        category = input(f"新分类 ({task.category}): ").strip() or task.category
        
        priority_options = [level.value for level in PriorityLevel]
        priority_input = input(f"新优先级 ({task.priority.value}) [{'/'.join(priority_options)}]: ").strip() or task.priority.value
        priority = PriorityLevel(priority_input)
        
        status_options = [status.value for status in TaskStatus]
        status_input = input(f"新状态 ({task.status.value}) [{'/'.join(status_options)}]: ").strip() or task.status.value
        status = TaskStatus(status_input)
        
        due_date_input = input(f"新截止日期 ({task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else '无'}): ").strip()
        due_date = task.due_date
        if due_date_input:
            try:
                due_date = datetime.strptime(due_date_input, "%Y-%m-%d %H:%M")
            except ValueError:
                print("日期格式无效，将保留原截止日期")
        
        task.update(
            title=title,
            description=description,
            category=category,
            priority=priority,
            status=status,
            due_date=due_date
        )
        
        if status == TaskStatus.DONE and not task.completed_at:
            task.mark_as_done()
        
        self.manager.save_tasks()
        print("\n✅ 任务更新成功！")
        print("更新后的任务信息:")
        print(task)

    def mark_task_done_ui(self) -> None:
        """标记任务为完成界面"""
        print("\n✅ 标记任务为完成")
        task_id = self.get_valid_input("请输入要标记的任务ID: ", int)
        task = self.manager.get_task_by_id(task_id)
        
        if not task:
            print("未找到该任务！")
            return
        
        if task.status == TaskStatus.DONE:
            print("该任务已经是完成状态！")
            return
        
        task.mark_as_done()
        self.manager.save_tasks()
        print(f"\n🎉 任务 '{task.title}' 已标记为完成！")

    def delete_task_ui(self) -> None:
        """删除任务界面"""
        print("\n🗑️ 删除任务")
        task_id = self.get_valid_input("请输入要删除的任务ID: ", int)
        self.manager.delete_task(task_id)

    def show_statistics_ui(self) -> None:
        """显示统计信息界面"""
        stats = self.manager.get_statistics()
        print("\n📊 任务统计信息")
        print("="*30)
        print(f"总任务数: {stats['total']}")
        print(f"待办任务: {stats['todo']}")
        print(f"进行中: {stats['in_progress']}")
        print(f"已完成: {stats['done']}")
        print(f"已取消: {stats['cancelled']}")
        print(f"逾期任务: {stats['overdue']}")
        print(f"完成率: {stats['completion_rate']:.1f}%")
        print("="*30)

    def run(self) -> None:
        """运行主程序"""
        print("🎉 欢迎使用待办事项管理系统！")
        
        while True:
            self.display_menu()
            choice = self.get_valid_input("请输入您的选择 (1-9): ", int, valid_options=list(range(1, 10)))
            
            if choice == 1:
                self.add_task_ui()
            elif choice == 2:
                tasks = self.manager.list_tasks()
                self.list_tasks_ui(tasks)
            elif choice == 3:
                status_options = [status.value for status in TaskStatus]
                status_input = self.get_valid_input(
                    f"请输入要筛选的状态 ({'/'.join(status_options)}): ",
                    valid_options=status_options
                )
                status = TaskStatus(status_input)
                tasks = self.manager.list_tasks(filter_status=status)
                self.list_tasks_ui(tasks)
            elif choice == 4:
                categories = self.manager.get_categories()
                if not categories:
                    print("\n📁 暂无分类")
                    continue
                print(f"\n📁 可用分类: {', '.join(categories)}")
                category = self.get_valid_input("请输入要筛选的分类: ", valid_options=categories)
                tasks = self.manager.list_tasks(filter_category=category)
                self.list_tasks_ui(tasks)
            elif choice == 5:
                self.update_task_ui()
            elif choice == 6:
                self.mark_task_done_ui()
            elif choice == 7:
                self.delete_task_ui()
            elif choice == 8:
                self.show_statistics_ui()
            elif choice == 9:
                print("\n👋 感谢使用待办事项管理系统，再见！")
                break


if __name__ == "__main__":
    ui = TaskManagerUI()
    ui.run()