from django.db import models

# Create your models here.
class Picture(models.Model):
    image = models.ImageField(upload_to='pics',verbose_name='图片')
    class Meta:
        db_table = 'tb_pics'
        verbose_name = '图片上传测试'
        verbose_name_plural = verbose_name