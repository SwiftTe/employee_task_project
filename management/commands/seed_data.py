from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tasks.models import Project, Task
from datetime import datetime, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with initial data for testing and development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create',
        )
        parser.add_argument(
            '--projects',
            type=int,
            default=5,
            help='Number of projects to create',
        )
        parser.add_argument(
            '--tasks',
            type=int,
            default=50,
            help='Number of tasks to create',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_data()
        
        num_users = options['users']
        num_projects = options['projects']
        num_tasks = options['tasks']
        
        self.stdout.write(self.style.SUCCESS(f'Starting database seeding...'))
        
        # Create users
        users = self.create_users(num_users)
        self.stdout.write(self.style.SUCCESS(f'Created {len(users)} users'))
        
        # Create projects
        projects = self.create_projects(num_projects, users)
        self.stdout.write(self.style.SUCCESS(f'Created {len(projects)} projects'))
        
        # Create tasks
        tasks = self.create_tasks(num_tasks, projects, users)
        self.stdout.write(self.style.SUCCESS(f'Created {len(tasks)} tasks'))
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))

    def clear_data(self):
        self.stdout.write('Clearing existing data...')
        Task.objects.all().delete()
        Project.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.WARNING('All data cleared'))

    def create_users(self, count):
        users = []
        departments = ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance']
        positions = ['Developer', 'Manager', 'Analyst', 'Designer', 'Tester']
        
        # Create admin user
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='admin123',
            role='ADMIN',
            is_staff=True,
            is_superuser=True
        )
        users.append(admin)
        
        # Create manager
        manager = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            first_name='Manager',
            last_name='User',
            password='manager123',
            role='MANAGER',
            is_staff=True
        )
        users.append(manager)
        
        # Create employees
        for i in range(count - 2):
            user = User.objects.create_user(
                username=f'employee{i+1}',
                email=f'employee{i+1}@example.com',
                first_name=f'First{i+1}',
                last_name=f'Last{i+1}',
                password='employee123',
                role='EMPLOYEE',
                department=random.choice(departments),
                position=random.choice(positions),
                date_joined_company=datetime.now().date() - timedelta(days=random.randint(30, 365))
            )
            users.append(user)
        
        return users

    def create_projects(self, count, users):
        projects = []
        managers = [u for u in users if u.role == 'MANAGER']
        
        for i in range(count):
            project = Project.objects.create(
                name=f'Project {i+1}',
                description=f'Description for Project {i+1}',
                start_date=datetime.now().date() - timedelta(days=random.randint(1, 30)),
                end_date=datetime.now().date() + timedelta(days=random.randint(30, 180)),
                created_by=random.choice(managers) if managers else users[0],
                is_active=True
            )
            projects.append(project)
        
        return projects

    def create_tasks(self, count, projects, users):
        tasks = []
        employees = [u for u in users if u.role == 'EMPLOYEE']
        managers = [u for u in users if u.role == 'MANAGER']
        
        priorities = ['LOW', 'MEDIUM', 'HIGH', 'URGENT']
        statuses = ['TODO', 'IN_PROGRESS', 'REVIEW', 'COMPLETED']
        
        for i in range(count):
            project = random.choice(projects)
            created_by = random.choice(managers) if managers else users[0]
            assigned_to = random.choice(employees) if employees and random.random() > 0.1 else None
            
            task = Task.objects.create(
                title=f'Task {i+1}',
                description=f'Description for Task {i+1}',
                project=project,
                created_by=created_by,
                assigned_to=assigned_to,
                priority=random.choice(priorities),
                status=random.choice(statuses),
                estimated_hours=random.uniform(1, 40),
                due_date=datetime.now() + timedelta(days=random.randint(1, 30))
            )
            
            # Set actual hours for completed tasks
            if task.status == 'COMPLETED':
                task.actual_hours = random.uniform(0.5, task.estimated_hours * 1.5)
                task.completed_at = datetime.now() - timedelta(days=random.randint(1, 10))
                task.save()
            
            tasks.append(task)
        
        return tasks
