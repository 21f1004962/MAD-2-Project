import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import AdminHomeView from '../views/AdminHomeView.vue'
import AdminRequestsView from '../views/AdminRequestsView.vue'
import RegisterView from '../views/RegisterView.vue'
import StoreManagerHomeView from '../views/StoreManagerHomeView.vue'
import StoreManagerProductsView from '../views/StoreManagerProductsView.vue'
import UserHomeView from '../views/UserHomeView.vue'
import UserCartView from '../views/UserCartView.vue'
import UserOrdersView from '../views/UserOrdersView.vue'
import UnauthorizedView from '../views/UnauthorizedView.vue'


const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/unauthorized',
    name: 'unauthorized',
    component: UnauthorizedView
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView
  },
  {
    path: '/adminHome',
    name: 'adminHome',
    component: AdminHomeView,
    meta: { requiresAuth: true, role: 'admin' }, // Requires authentication and admin role

  },
  {
    path: '/adminRequests',
    name: 'adminRequests',
    component: AdminRequestsView,
    meta: { requiresAuth: true, role: 'admin' }, // Requires authentication and admin role
  },
  {
    path: '/storeManagerHome',
    name: 'storeManagerHome',
    component: StoreManagerHomeView,
    meta: { requiresAuth: true, role: 'storeManager' },

  },
  {
    path: '/storeManagerProducts/:CategoryId',
    name: 'storeManagerProducts',
    component: StoreManagerProductsView,
    meta: { requiresAuth: true, role: 'storeManager' },
    props: true,
  },
  {
    path: '/userHome/:searchType?/:searchQuery?',
    name: 'userHome',
    component: UserHomeView,
    meta: { requiresAuth: true, role: 'user' },
    props: true,
  },
  {
    path: '/userCart',
    name: 'userCart',
    component: UserCartView,
    meta: { requiresAuth: true, role: 'user' },
  },
  {
    path: '/userOrders',
    name: 'userOrders',
    component: UserOrdersView,
    meta: { requiresAuth: true, role: 'user' },
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// function parseJwt (token) {
//   var base64Url = token.split('.')[1];
//   var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
//   var jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
//       return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
//   }).join(''));

//   return JSON.parse(jsonPayload);
// }

router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const roleRequired = to.matched.some(record => record.meta.role);

  const jwtToken = localStorage.getItem('jwtToken');

  if (requiresAuth) {
    if (!jwtToken) {
      next('/login');
    } else {
      try {
        const decodedToken = JSON.parse(atob(jwtToken.split('.')[1]));

        if (Date.now() >= decodedToken.exp * 1000) {
          console.error('Token is expired');
          localStorage.removeItem('jwtToken');
          next('/login');
        } else if (roleRequired && decodedToken.role !== to.meta.role) {
          next('/unauthorized');
        } else {
          next();
        }
      } catch (error) {
        console.error('Error decoding token:', error);
        localStorage.removeItem('jwtToken');
        next('/login');
      }
    }
  } else {
    next();
  }
});

export default router
