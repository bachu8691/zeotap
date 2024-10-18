from django.db import models

class Node(models.Model):
    TYPE_CHOICES = [
        ('operator', 'Operator'),
        ('operand', 'Operand')
    ]
    
    OPERATOR_CHOICES = [
        ('AND', 'AND'),
        ('OR', 'OR'),
        ('>', 'Greater than'),
        ('<', 'Less than'),
        ('=', 'Equal'),
    ]
    
    type = models.CharField(max_length=50)
    operator = models.CharField(max_length=50, null=True, blank=True)
    value = models.CharField(max_length=100, null=True, blank=True)
    left = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='left_node')
    right = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='right_node')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='parent_node')
    
    def __str__(self):
        return f"{self.type} - {self.operator or self.value}"
