import { request } from '@/utils'

export default {
  login: (data) => request.post('/base/access_token', data, { noNeedToken: true }),
  getUserInfo: () => request.get('/base/userinfo'),
  getUserMenu: () => request.get('/base/usermenu'),
  getUserApi: () => request.get('/base/userapi'),
  // profile
  updatePassword: (data = {}) => request.post('/base/update_password', data),
  // users
  getUserList: (params = {}) => request.get('/user/list', { params }),
  getUserById: (params = {}) => request.get('/user/get', { params }),
  createUser: (data = {}) => request.post('/user/create', data),
  updateUser: (data = {}) => request.post('/user/update', data),
  deleteUser: (params = {}) => request.delete(`/user/delete`, { params }),
  resetPassword: (data = {}) => request.post(`/user/reset_password`, data),
  // role
  getRoleList: (params = {}) => request.get('/role/list', { params }),
  createRole: (data = {}) => request.post('/role/create', data),
  updateRole: (data = {}) => request.post('/role/update', data),
  deleteRole: (params = {}) => request.delete('/role/delete', { params }),
  updateRoleAuthorized: (data = {}) => request.post('/role/authorized', data),
  getRoleAuthorized: (params = {}) => request.get('/role/authorized', { params }),
  // menus
  getMenus: (params = {}) => request.get('/menu/list', { params }),
  createMenu: (data = {}) => request.post('/menu/create', data),
  updateMenu: (data = {}) => request.post('/menu/update', data),
  deleteMenu: (params = {}) => request.delete('/menu/delete', { params }),
  // apis
  getApis: (params = {}) => request.get('/api/list', { params }),
  createApi: (data = {}) => request.post('/api/create', data),
  updateApi: (data = {}) => request.post('/api/update', data),
  deleteApi: (params = {}) => request.delete('/api/delete', { params }),
  refreshApi: (data = {}) => request.post('/api/refresh', data),
  // depts
  getDepts: (params = {}) => request.get('/dept/list', { params }),
  createDept: (data = {}) => request.post('/dept/create', data),
  updateDept: (data = {}) => request.post('/dept/update', data),
  deleteDept: (params = {}) => request.delete('/dept/delete', { params }),
  // auditlog
  getAuditLogList: (params = {}) => request.get('/auditlog/list', { params }),
  // product categories
  getProductCategoryList: (params = {}) => request.get('/product-category/list', { params }),
  createProductCategory: (data = {}, params = {}) =>
    request.post('/product-category/create', data, { params }),
  updateProductCategory: (data = {}, params = {}) =>
    request.post('/product-category/update', data, { params }),
  deleteProductCategory: (params = {}) => request.delete('/product-category/delete', { params }),
  // products
  getProductList: (params = {}) => request.get('/product/list', { params }),
  getProductById: (params = {}) => request.get('/product/get', { params }),
  createProduct: (data = {}, params = {}) => request.post('/product/create', data, { params }),
  updateProduct: (data = {}, params = {}) => request.post('/product/update', data, { params }),
  changeProductStatus: (data = {}, params = {}) =>
    request.post('/product/change_status', data, { params }),
  // inventories
  getInventoryBalanceList: (params = {}) => request.get('/inventory/balance/list', { params }),
  getInventoryTxnList: (params = {}) => request.get('/inventory/txn/list', { params }),
  getInventoryWarningList: (params = {}) => request.get('/inventory/warning/list', { params }),
  // finance
  getFinanceOverview: (params = {}) => request.get('/finance/overview', { params }),
  getFinanceStatementList: (params = {}) => request.get('/finance/statement/list', { params }),
  // members
  getMemberList: (params = {}) => request.get('/member/list', { params }),
  getMemberById: (params = {}) => request.get('/member/get', { params }),
  createMember: (data = {}, params = {}) => request.post('/member/create', data, { params }),
  updateMember: (data = {}, params = {}) => request.post('/member/update', data, { params }),
  deleteMember: (params = {}) => request.delete('/member/delete', { params }),
  // store employees
  getStoreEmployeeList: (params = {}) => request.get('/store-employee/list', { params }),
  getStoreEmployeeById: (params = {}) => request.get('/store-employee/get', { params }),
  createStoreEmployee: (data = {}, params = {}) => request.post('/store-employee/create', data, { params }),
  updateStoreEmployee: (data = {}, params = {}) => request.post('/store-employee/update', data, { params }),
  deleteStoreEmployee: (params = {}) => request.delete('/store-employee/delete', { params }),
  // suppliers
  getSupplierList: (params = {}) => request.get('/supplier/list', { params }),
  getSupplierById: (params = {}) => request.get('/supplier/get', { params }),
  createSupplier: (data = {}, params = {}) => request.post('/supplier/create', data, { params }),
  updateSupplier: (data = {}, params = {}) => request.post('/supplier/update', data, { params }),
  deleteSupplier: (params = {}) => request.delete('/supplier/delete', { params }),
}
