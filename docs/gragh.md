gantt
    title 超市管理系统（三组并行）- 26工作日计划
    dateFormat  YYYY-MM-DD
    axisFormat  %m/%d

    section 共享/架构
    A0 需求冻结与数据边界         :a0, 2026-03-23, 2d
    D1 跨组联调与验收             :d1, after c4, 3d
    D2 性能回归与上线清单         :d2, after d1, 2d

    section 第1组 登录注册
    A1 鉴权扩展(store_id策略)      :a1, after a0, 2d
    A2 注册/员工开户流程           :a2, after a1, 4d
    A3 角色权限与菜单落地          :a3, after a2, 2d

    section 第2组 商品管理
    B1 商品域模型与迁移            :b1, after a1, 3d
    B2 商品管理API                 :b2, after b1, 4d
    B3 商品管理前端页              :b3, after b2, 4d

    section 第3组 库存与流水
    C1 库存流水模型与迁移          :c1, after b1, 3d
    C2 库存变更服务(防负库存)      :c2, after c1, 4d
    C3 日/周/月流水聚合API         :c3, after c2, 3d
    C4 库存与流水看板前端          :c4, after c3, 4d
