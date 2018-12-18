"""
python manage.py inspectdb --database backend > backend/models.py
"""
from django.db import models


class Dept(models.Model):
    no = models.IntegerField(primary_key=True, db_column='dno')
    name = models.CharField(unique=True, max_length=10, db_column='dname')
    loc = models.CharField(max_length=20, db_column='dloc')

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        app_label = 'hrs'
        db_table = 'TbDept'


# 查询编号为20的部门的员工
# Dept.objects.get(no=20).emp_set.all()
# Emp.objects.filter(dept__no=20)
# 如果不想通过xxx_set属性从一方查询多方可以在设置ForeignKey时
# 将related_name设置为'+'
class Emp(models.Model):
    no = models.IntegerField(primary_key=True, db_column='eno')
    name = models.CharField(max_length=20, db_column='ename')
    job = models.CharField(max_length=20)
    mgr = models.ForeignKey('self', models.PROTECT, db_column='mgr', blank=True, null=True)
    sal = models.IntegerField()
    comm = models.IntegerField(blank=True, null=True)
    dept = models.ForeignKey('Dept', models.DO_NOTHING, db_column='dno', related_name='+', blank=True, null=True)

    class Meta:
        managed = False
        app_label = 'hrs'
        db_table = 'TbEmp'
