from tortoise import fields

from app.schemas.menus import MenuType

from .base import BaseModel, TimestampMixin
from .enums import MethodType


class User(BaseModel, TimestampMixin):
    username = fields.CharField(max_length=20, unique=True, description="用户名称", index=True)
    alias = fields.CharField(max_length=30, null=True, description="姓名", index=True)
    email = fields.CharField(max_length=255, unique=True, description="邮箱", index=True)
    phone = fields.CharField(max_length=20, null=True, description="电话", index=True)
    password = fields.CharField(max_length=128, null=True, description="密码")
    is_active = fields.BooleanField(default=True, description="是否激活", index=True)
    is_superuser = fields.BooleanField(default=False, description="是否为超级管理员", index=True)
    last_login = fields.DatetimeField(null=True, description="最后登录时间", index=True)
    roles = fields.ManyToManyField("models.Role", related_name="user_roles")
    dept_id = fields.IntField(null=True, description="部门ID", index=True)

    class Meta:
        table = "user"


class Role(BaseModel, TimestampMixin):
    name = fields.CharField(max_length=20, unique=True, description="角色名称", index=True)
    desc = fields.CharField(max_length=500, null=True, description="角色描述")
    menus = fields.ManyToManyField("models.Menu", related_name="role_menus")
    apis = fields.ManyToManyField("models.Api", related_name="role_apis")

    class Meta:
        table = "role"


class Api(BaseModel, TimestampMixin):
    path = fields.CharField(max_length=100, description="API路径", index=True)
    method = fields.CharEnumField(MethodType, description="请求方法", index=True)
    summary = fields.CharField(max_length=500, description="请求简介", index=True)
    tags = fields.CharField(max_length=100, description="API标签", index=True)

    class Meta:
        table = "api"


class Menu(BaseModel, TimestampMixin):
    name = fields.CharField(max_length=20, description="菜单名称", index=True)
    remark = fields.JSONField(null=True, description="保留字段")
    menu_type = fields.CharEnumField(MenuType, null=True, description="菜单类型")
    icon = fields.CharField(max_length=100, null=True, description="菜单图标")
    path = fields.CharField(max_length=100, description="菜单路径", index=True)
    order = fields.IntField(default=0, description="排序", index=True)
    parent_id = fields.IntField(default=0, description="父菜单ID", index=True)
    is_hidden = fields.BooleanField(default=False, description="是否隐藏")
    component = fields.CharField(max_length=100, description="组件")
    keepalive = fields.BooleanField(default=True, description="存活")
    redirect = fields.CharField(max_length=100, null=True, description="重定向")

    class Meta:
        table = "menu"


class Dept(BaseModel, TimestampMixin):
    name = fields.CharField(max_length=20, unique=True, description="部门名称", index=True)
    desc = fields.CharField(max_length=500, null=True, description="备注")
    is_deleted = fields.BooleanField(default=False, description="软删除标记", index=True)
    order = fields.IntField(default=0, description="排序", index=True)
    parent_id = fields.IntField(default=0, max_length=10, description="父部门ID", index=True)

    class Meta:
        table = "dept"


class DeptClosure(BaseModel, TimestampMixin):
    ancestor = fields.IntField(description="父代", index=True)
    descendant = fields.IntField(description="子代", index=True)
    level = fields.IntField(default=0, description="深度", index=True)


class AuditLog(BaseModel, TimestampMixin):
    user_id = fields.IntField(description="用户ID", index=True)
    username = fields.CharField(max_length=64, default="", description="用户名称", index=True)
    module = fields.CharField(max_length=64, default="", description="功能模块", index=True)
    summary = fields.CharField(max_length=128, default="", description="请求描述", index=True)
    method = fields.CharField(max_length=10, default="", description="请求方法", index=True)
    path = fields.CharField(max_length=255, default="", description="请求路径", index=True)
    status = fields.IntField(default=-1, description="状态码", index=True)
    response_time = fields.IntField(default=0, description="响应时间(单位ms)", index=True)
    request_args = fields.JSONField(null=True, description="请求参数")
    response_body = fields.JSONField(null=True, description="返回数据")


class ProductCategory(BaseModel, TimestampMixin):
    store_id = fields.IntField(description="门店ID", index=True)
    name = fields.CharField(max_length=64, description="分类名称", index=True)
    sort = fields.IntField(default=0, description="排序", index=True)
    status = fields.BooleanField(default=True, description="状态", index=True)

    class Meta:
        table = "product_category"
        unique_together = ("store_id", "name")
        indexes = (("store_id", "status"), ("store_id", "sort"))


class Product(BaseModel, TimestampMixin):
    store_id = fields.IntField(description="门店ID", index=True)
    category_id = fields.IntField(description="分类ID", index=True)
    product_code = fields.CharField(max_length=64, description="商品编码", index=True)
    name = fields.CharField(max_length=128, description="商品名称", index=True)
    barcode = fields.CharField(max_length=64, null=True, description="条码", index=True)
    unit = fields.CharField(max_length=16, description="单位")
    sale_price = fields.DecimalField(max_digits=10, decimal_places=2, description="售价", index=True)
    status = fields.BooleanField(default=True, description="上架状态", index=True)
    stock_status = fields.BooleanField(default=True, description="库存状态", index=True)
    low_stock_threshold = fields.IntField(default=0, description="预警阈值", index=True)
    remark = fields.CharField(max_length=255, null=True, description="备注")

    class Meta:
        table = "product"
        unique_together = (("store_id", "product_code"), ("store_id", "barcode"))
        indexes = (("store_id", "status"), ("store_id", "category_id"), ("store_id", "stock_status"))


class StoreInventory(BaseModel, TimestampMixin):
    store_id = fields.IntField(description="门店ID", index=True)
    product_id = fields.IntField(description="商品ID", index=True)
    available_qty = fields.IntField(default=0, description="可用库存", index=True)
    locked_qty = fields.IntField(default=0, description="锁定库存")
    low_stock_threshold = fields.IntField(default=0, description="预警阈值", index=True)
    version = fields.IntField(default=1, description="乐观锁版本")
    updated_by = fields.IntField(null=True, description="更新人", index=True)

    class Meta:
        table = "store_inventory"
        unique_together = ("store_id", "product_id")
        indexes = (("store_id", "available_qty"), ("store_id", "low_stock_threshold"))


class InventoryTxn(BaseModel, TimestampMixin):
    store_id = fields.IntField(description="门店ID", index=True)
    product_id = fields.IntField(description="商品ID", index=True)
    biz_type = fields.CharField(max_length=32, description="业务类型", index=True)
    biz_no = fields.CharField(max_length=64, description="业务单号", index=True)
    change_qty = fields.IntField(description="变更数量", index=True)
    before_qty = fields.IntField(description="变更前数量")
    after_qty = fields.IntField(description="变更后数量", index=True)
    remark = fields.CharField(max_length=255, null=True, description="备注")
    operator_id = fields.IntField(null=True, description="操作人", index=True)

    class Meta:
        table = "inventory_txn"
        indexes = (("store_id", "created_at"), ("store_id", "product_id", "created_at"))


class Member(BaseModel, TimestampMixin):
    store_id = fields.IntField(description="门店ID", index=True)
    member_no = fields.CharField(max_length=32, description="会员编号", index=True)
    name = fields.CharField(max_length=64, description="会员姓名", index=True)
    phone = fields.CharField(max_length=20, null=True, description="手机号", index=True)
    level = fields.CharField(max_length=32, default="NORMAL", description="会员等级", index=True)
    points = fields.IntField(default=0, description="积分", index=True)
    status = fields.BooleanField(default=True, description="状态", index=True)
    remark = fields.CharField(max_length=255, null=True, description="备注")

    class Meta:
        table = "member"
        unique_together = (("store_id", "member_no"),)
        indexes = (("store_id", "status"), ("store_id", "level"))


class StoreEmployee(BaseModel, TimestampMixin):
    store_id = fields.IntField(description="门店ID", index=True)
    employee_no = fields.CharField(max_length=32, description="员工工号", index=True)
    name = fields.CharField(max_length=64, description="员工姓名", index=True)
    phone = fields.CharField(max_length=20, null=True, description="手机号", index=True)
    job_title = fields.CharField(max_length=64, description="岗位", index=True)
    hire_date = fields.DateField(null=True, description="入职日期")
    status = fields.BooleanField(default=True, description="状态", index=True)
    remark = fields.CharField(max_length=255, null=True, description="备注")

    class Meta:
        table = "store_employee"
        unique_together = (("store_id", "employee_no"),)
        indexes = (("store_id", "status"), ("store_id", "job_title"))


class Supplier(BaseModel, TimestampMixin):
    store_id = fields.IntField(description="门店ID", index=True)
    supplier_code = fields.CharField(max_length=32, description="供应商编码", index=True)
    supplier_name = fields.CharField(max_length=128, description="供应商名称", index=True)
    contact_name = fields.CharField(max_length=64, null=True, description="联系人")
    phone = fields.CharField(max_length=20, null=True, description="联系电话", index=True)
    settlement_cycle = fields.IntField(default=30, description="结算周期(天)")
    status = fields.BooleanField(default=True, description="状态", index=True)
    address = fields.CharField(max_length=255, null=True, description="地址")
    remark = fields.CharField(max_length=255, null=True, description="备注")

    class Meta:
        table = "supplier"
        unique_together = (("store_id", "supplier_code"),)
        indexes = (("store_id", "status"), ("store_id", "supplier_name"))
