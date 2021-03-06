- 手机端功能
    - 用户功能
        - 注册
            - dependency
                - fastapi-users
            - router
                - /api/app/users/register
                - POST
                - 手机或邮箱注册
                - email register
                - phone register
            - router
                - /api/app/get_verify_code
                - POST
                - 获取验证码
            - router
                - /api/app/verify
                - POST
                - 进行验证
        - 登陆
            - dependency
                - fastapi-users
            - router
                - /api/app/users/login
                - POST
                - 用户登陆
            - router
                - /api/app/users/logout
                - POST
                - 注销登陆/退出登陆
        - 忘记密码和修改密码
            - router
                - /api/app/users/forgot-password
                - POST
                - 忘记密码
            - router
                - /api/app/users/reset-password
                - POST
                - 重置密码
    - 用户信息功能
        - 头像
            - router 
                - /api/app/user_info/avatar
                - GET
                - 获取用户头像
            - router
                - /api/app/user_info/avatar/upload
                - POST
                - 上传用户头像
        - 个人信息
            - 基础信息
                - router
                    - /api/app/user_info/gprofile
                    - GET
                    - 获取个人信息
                - router
                    - /api/app/user_info/set_profile
                    - POST
                    - 设置修改个人信息
                - content
                    - 头像
                    - 昵称
                    - 性别
                    - 地区
                    - 个性签名   
            - 资产信息概况
                - router
                    - /api/app/user_info/simple_info
                    - GET
                    - 获取昵称和资产
            - 分享邀请码
                - router
                    - /api/app/user_info/share
                    - GET
                    - 邀请码
            - 地址信息
                - router
                    - /api/app/user_info/add_update_address
                    - POST
                    - 添加或更换地址
                - router
                    - /api/app/user_info/get_address
                    - GET
                    - 获取用户地址
                - router
                    - /api/app/user_info/delete_address
                    - GET
                    - 删除用户地址
    - 团队功能
        - router
            - /api/app/team/members
            - GET
            - 获取团队成员
    - 收益功能
        - router
            - /api/app/reward/home_reward
            - GET
            - 首页收益
        - route
            - /api/app/reward/abs_reward
            - GET
            - 收益概况
        - router
            - /api/app/reward/my_miner
            - GET
            - 我的机器
        - router
            - /api/app/reward/miner_reward
            - GET
            - 机器收益
        - router
            - /api/app/reward/team_miner_reward
            - GET
            - 团队机器收益
    - 客户服务功能
        - router
            - /api/app/csc/announcement/list
            - GET
            - 获取公告列表
        - router
            - /api/app/csc/announcement/{announcement_id}
            - GET
            - 获取公告详情
        - router
            - /api/app/csc/customer_urls
            - GET
            - 获取客服服务链接
    - 交易功能
        - router
            - /api/app/exchange/personal_miner
            - GET
            - 获取个人机器
        - router
            - /api/app/exchange/team_miners
            - GET
            - 获取参与的团队机器
        - router
            - /api/app/exchange/miner/{miner_name}
            - GET
            - 获取个人购买机器详情
        - router
            - /api/app/exchange/team_miner/{miner_name}
            - GET
            - 获取组团购买机器详情
        - router
            - /api/app/exchange/buy_miner
            - POST
            - 个人购买机器
        - router
            - /api/app/exchange/share_buy
            - POST
            - 生成组团购买邀请码和邀请链接
        - router
            - /api/app/exchange/get_share_code
            - GET
            - 获取组团邀请码
        - router
            - /api/app/exchange/share/{share_code}
            - GET
            - 点击组团购买邀请链接
        - router
            - /api/app/exchange/share_monitor/{share_code}
            - GET
            - 主动获取拼团购买状态
        - router
            - /api/app/exchange/team_share_buy
            - POST
            - 拼团购买机器付款
        - router
            - /api/app/exchange/recharge
            - POST
            - 充值
        - router
            - /api/app/exchange/withdraw
            - POST
            - 提现
        - router
            - /api/app/exchange/record
            - POST
            - 记录查询(充值、提现、个人机器收益、拼团机器收益)
    - Code Ref:
        - Error Code:
            - 200: User does not exist, please register first!
            - 201: Account was locked，please contact customer service!
            - 203: Password cannot be empty!
            - 204: Two password are not the same, please check!!
            - 205: 
                - Nickname was already used!
                - Email was already used!
                - Phone was already used!
            - 206:
                - Please enter right email address!
                - Please enter right phone number! 
            - 207:
                - The number of login times has exceeded the limit, and the account has been locked!
                - Password was incorrect，only xxx times to retry!
            - 208:
                - Old password was incorrect, please try again!
            - 209:
                - Order created failed, your balance is not enough to buy, please recharge!
            - 210:
                - Unbinding address!
            - 211:
                - Number of buyers exceeded!
            - 212:
                - Share buy url was expired!
            - 213:
                - Out of level range!

- 后台管理功能
    - 用户管理(加入会员标识和等级标识，支持修改默认密码，存储为密文，故只能用来重置初始密码)
        - 查看所有用户信息
        - 查询单一用户信息
            - 用户ID
            - 昵称
            - 手机号
            - Email
            - 注册时邀请码
            - 推荐码
            - 注册时间
            - 最近一次登陆时间
            - 最近一次登陆IP
            - 登陆状态
            - 是否通过验证
            - 用户状态(是否被锁定)
            - 会员状态
            - 等级状态
        - 更新单一用户信息(包括重置单一用户密码)
        - 删除单一用户信息
        - 新增单一用户信息
        - 会员状态管理
        - 等级信息管理
    - 会员管理(暂时不需要，融合进用户管理)
    - 等级管理(暂时不需要，融合进用户管理)
    - 机器管理(个人和拼团)
        - 查看所有机器
        - 查看单一机器信息
            - 机器名称
            - 机器算力
            - 机器预期月收益
            - 机器剩余数量
            - 机器总量
            - 机器销售数量
            - 机器价格
                - 个人购买和团购价格
            - 机器托管费用(百分比)
            - 机器图片
        - 新增单一机器信息
        - 删除单一机器信息
        - 更新单一机器信息
    - 资金明细
        - 查看单一用户/团队充值明细记录
        - 查看单一用户/团队提现明细记录
        - 查看单一用户/团队收益明细记录
        - 查看单一用户/团队购买明细记录
        - 导出为Excel或CSV(暂时不做)
    - 积分明细(暂时不需要)
    - 活动管理
        - 显示所有活动
        - 查询单一活动
            - 活动标题
            - 活动ID
            - 活动详情
            - 创建人
            - 创建时间
            - 有效期(暂时不需要)
            - 截止日期(暂时不需要)
        - 新增单一活动
        - 删除单一活动
        - 更新单一活动
    - 公告(和活动管理基本一致)
        - 显示所有公告
        - 查询单一公告
            - 公告标题
            - 公告ID
            - 公告详情
            - 创建人
            - 创建时间
        - 新增单一公告
        - 删除单一公告
        - 更新单一公告
    - 权限管理
       - user(app-user)
            - privilege
                - 无权限
            - 列出所有user_id、用户状态、注册时间
       - superuser(超级管理员)
           - privilege
                - 用户管理权限(app-user)
                - 系统设置权限(web)
                - 活动管理权限
                - 公告管理权限
                - 机器管理权限
                - 资金明细管理权限
       - genuser(普通管理员)
           - privilege
                - 用户管理权限(app-user)
                - 活动管理权限
                - 公告管理权限
                - 机器管理权限
                - 资金明细管理权限
    - 系统配置
        - 管理员登录
        - 管理员登出
        - 重置管理员密码
        - 忘记管理员密码
        - 新增管理员账户
        - 删除管理员账户
        - 业务初始配置
        - 系统信息配置(暂时忽略设置内容)

