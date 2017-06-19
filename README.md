# Wenda-Python
根据Flask web开发一书小改动了下完成的毕设
系统有六个类。用户，具有登录、登出、注册、确认邮箱、修改密码、修改资料的方法；问题，具有提问、编辑问题、全部问题的方法，是在首页进行提问，所以为index()；回答，具有回答、编辑回答可见性的方法；关注有关注和取关，查看关注者和被关注者的功能；搜索有搜索功能。
（1）	程序一般保存在app包中；magrations包含数据库迁移脚本；venv包含了虚拟环境；requirements.txt列出项目所需所有依赖包，便于在其他电脑中生成相同虚拟环境；config.py存储配置信息；manage.py用于启动程序[8]。
（2）	app包中，包含了所有显示页面的templates；静态文件的static；主要文件main文件夹；数据库模型models.py；支持电子邮件的emails.py。
（3）	 main中，包含了各种功能的表单的forms.py；route装饰器定义认证路由相关的views.py。
