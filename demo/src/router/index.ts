import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import SportView from '../views/SportView.vue'
import LiveView from '../views/LiveView.vue'
import PromotionsView from '../views/PromotionsView.vue'
import ProfileView from '../views/ProfileView.vue'
import PortalView from '../views/PortalView.vue'
import ImpactView from '../views/ImpactView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/sport', name: 'sport', component: SportView },
    { path: '/live', name: 'live', component: LiveView },
    { path: '/promotions', name: 'promotions', component: PromotionsView },
    { path: '/profile', name: 'profile', component: ProfileView },
    { path: '/portal', name: 'portal', component: PortalView },
    { path: '/portal/analytics', name: 'portal-analytics', component: PortalView },
    { path: '/impact', name: 'impact', component: ImpactView },
    { path: '/analytics/impact', name: 'analytics-impact', component: ImpactView },
  ],
})

export default router
