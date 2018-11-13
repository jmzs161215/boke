# 针对用户业务逻辑处理的视图和路由的定义
from . import user

@user.route('/user')
def user_index():
  return "这是user应用中的首页"