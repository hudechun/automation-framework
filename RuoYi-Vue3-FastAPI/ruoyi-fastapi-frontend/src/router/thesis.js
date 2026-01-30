import Layout from '@/layout'

/**
 * AI论文写作系统路由配置
 * 
 * 注意：RuoYi使用动态路由系统，路由从后端菜单数据动态生成
 * 此文件仅用于组件路径映射参考
 */

// 论文系统路由配置
export const thesisRoutes = {
  path: '/thesis',
  component: Layout,
  redirect: '/thesis/member/package',
  name: 'Thesis',
  meta: {
    title: 'AI论文写作',
    icon: 'education'
  },
  children: [
    // 会员管理
    {
      path: 'member',
      name: 'ThesisMember',
      meta: { title: '会员管理', icon: 'peoples' },
      children: [
        {
          path: 'package',
          name: 'MemberPackage',
          component: () => import('@/views/thesis/member/package'),
          meta: { title: '会员套餐', icon: 'shopping' }
        },
        {
          path: 'user',
          name: 'MemberUser',
          component: () => import('@/views/thesis/member/user'),
          meta: { title: '用户会员', icon: 'user' }
        },
        {
          path: 'quota',
          name: 'MemberQuota',
          component: () => import('@/views/thesis/member/quota'),
          meta: { title: '配额管理', icon: 'chart' }
        }
      ]
    },
    // 论文管理
    {
      path: 'paper',
      name: 'ThesisPaper',
      meta: { title: '论文管理', icon: 'documentation' },
      children: [
        {
          path: 'list',
          name: 'PaperList',
          component: () => import('@/views/thesis/paper/list'),
          meta: { title: '论文列表', icon: 'list' }
        }
      ]
    },
    // 模板管理
    {
      path: 'template',
      name: 'ThesisTemplate',
      meta: { title: '模板管理', icon: 'component' },
      children: [
        {
          path: 'list',
          name: 'TemplateList',
          component: () => import('@/views/thesis/template/list'),
          meta: { title: '模板列表', icon: 'list' }
        }
      ]
    },
    // 大纲提示词模板
    {
      path: 'outline-prompt-template',
      name: 'OutlinePromptTemplate',
      component: () => import('@/views/thesis/outline-prompt-template/index'),
      meta: { title: '大纲提示词模板', icon: 'documentation' }
    },
    // 订单管理
    {
      path: 'order',
      name: 'ThesisOrder',
      meta: { title: '订单管理', icon: 'shopping' },
      children: [
        {
          path: 'list',
          name: 'OrderList',
          component: () => import('@/views/thesis/order/list'),
          meta: { title: '订单列表', icon: 'list' }
        }
      ]
    },
    // 支付管理
    {
      path: 'payment',
      name: 'ThesisPayment',
      meta: { title: '支付管理', icon: 'money' },
      children: [
        {
          path: 'config',
          name: 'PaymentConfig',
          component: () => import('@/views/thesis/payment/config'),
          meta: { title: '支付配置', icon: 'tool' }
        },
        {
          path: 'transaction',
          name: 'PaymentTransaction',
          component: () => import('@/views/thesis/payment/transaction'),
          meta: { title: '交易记录', icon: 'list' }
        }
      ]
    }
  ]
}

/**
 * 组件路径映射表
 * 用于动态路由组件加载
 */
export const thesisComponentMap = {
  // 会员管理
  'thesis/member/package': () => import('@/views/thesis/member/package'),
  'thesis/member/user': () => import('@/views/thesis/member/user'),
  'thesis/member/quota': () => import('@/views/thesis/member/quota'),
  
  // 论文管理
  'thesis/paper/list': () => import('@/views/thesis/paper/list'),
  
  // 模板管理
  'thesis/template/list': () => import('@/views/thesis/template/list'),
  
  // 大纲提示词模板
  'thesis/outline-prompt-template': () => import('@/views/thesis/outline-prompt-template/index'),
  
  // 订单管理
  'thesis/order/list': () => import('@/views/thesis/order/list'),
  
  // 支付管理
  'thesis/payment/config': () => import('@/views/thesis/payment/config'),
  'thesis/payment/transaction': () => import('@/views/thesis/payment/transaction'),
  
  // AI模型配置
  'thesis/ai-model/config': () => import('@/views/thesis/ai-model/config')
}

export default thesisRoutes
