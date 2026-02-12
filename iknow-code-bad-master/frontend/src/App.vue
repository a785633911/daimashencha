<template>
  <div id="app">
    <el-container style="height: 100vh">
      <el-aside width="260px" class="sidebar">
        <div class="logo-container">
          <svg class="logo-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 12L11 14L15 10M7.835 4.697C8.791 3.602 9.269 3.055 9.866 2.715C10.392 2.416 10.977 2.25 11.575 2.228C12.257 2.203 12.977 2.448 14.417 2.938L16.3 3.617C17.74 4.107 18.46 4.352 19.005 4.807C19.487 5.208 19.872 5.717 20.13 6.292C20.423 6.948 20.5 7.722 20.654 9.27L20.808 10.818C20.962 12.366 21.039 13.14 20.866 13.838C20.715 14.451 20.424 15.021 20.018 15.502C19.556 16.046 18.866 16.391 17.486 17.081L15.7 17.97C14.32 18.66 13.63 19.005 12.898 19.127C12.248 19.236 11.582 19.236 10.932 19.127C10.2 19.005 9.51 18.66 8.13 17.97L6.344 17.081C4.964 16.391 4.274 16.046 3.812 15.502C3.406 15.021 3.115 14.451 2.964 13.838C2.791 13.14 2.868 12.366 3.022 10.818L3.176 9.27C3.33 7.722 3.407 6.948 3.7 6.292C3.958 5.717 4.343 5.208 4.825 4.807C5.37 4.352 6.09 4.107 7.53 3.617L9.413 2.938C10.853 2.448 11.573 2.203 12.255 2.228C12.853 2.25 13.438 2.416 13.964 2.715C14.561 3.055 15.039 3.602 15.995 4.697L7.835 4.697Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <div class="logo-text">MyBrokenCode</div>
        </div>
        <el-menu
          :default-active="$route.path"
          router
          background-color="transparent"
          text-color="#8B7355"
          active-text-color="#FF8C42"
          class="sidebar-menu"
        >
          <el-menu-item index="/ai-config" class="menu-item">
            <svg class="menu-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M18.7273 14.7273C18.6063 15.0015 18.5702 15.3056 18.6236 15.6005C18.6771 15.8954 18.8177 16.1676 19.0273 16.3818L19.0818 16.4364C19.2509 16.6052 19.385 16.8057 19.4765 17.0265C19.568 17.2472 19.6151 17.4838 19.6151 17.7227C19.6151 17.9617 19.568 18.1983 19.4765 18.419C19.385 18.6397 19.2509 18.8402 19.0818 19.0091C18.913 19.1781 18.7124 19.3122 18.4917 19.4037C18.271 19.4952 18.0344 19.5423 17.7955 19.5423C17.5565 19.5423 17.3199 19.4952 17.0992 19.4037C16.8785 19.3122 16.678 19.1781 16.5091 19.0091L16.4545 18.9545C16.2403 18.745 15.9682 18.6044 15.6733 18.5509C15.3784 18.4974 15.0742 18.5335 14.8 18.6545C14.5311 18.7698 14.3018 18.9611 14.1403 19.205C13.9788 19.4489 13.8921 19.7347 13.8909 20.0273V20.1818C13.8909 20.664 13.6994 21.1265 13.3584 21.4675C13.0174 21.8084 12.5549 22 12.0727 22C11.5905 22 11.1281 21.8084 10.7871 21.4675C10.4461 21.1265 10.2545 20.664 10.2545 20.1818V20.1C10.2475 19.7991 10.1501 19.5073 9.97501 19.2625C9.79991 19.0176 9.55521 18.8312 9.27273 18.7273C8.99853 18.6063 8.69437 18.5702 8.39947 18.6236C8.10456 18.6771 7.83244 18.8177 7.61818 19.0273L7.56364 19.0818C7.39478 19.2509 7.19425 19.385 6.97353 19.4765C6.7528 19.568 6.51621 19.6151 6.27727 19.6151C6.03834 19.6151 5.80174 19.568 5.58102 19.4765C5.36029 19.385 5.15977 19.2509 4.99091 19.0818C4.82186 18.913 4.68775 18.7124 4.59626 18.4917C4.50476 18.271 4.45766 18.0344 4.45766 17.7955C4.45766 17.5565 4.50476 17.3199 4.59626 17.0992C4.68775 16.8785 4.82186 16.678 4.99091 16.5091L5.04545 16.4545C5.25503 16.2403 5.39562 15.9682 5.4491 15.6733C5.50257 15.3784 5.46647 15.0742 5.34545 14.8C5.23022 14.5311 5.03887 14.3018 4.79497 14.1403C4.55107 13.9788 4.26526 13.8921 3.97273 13.8909H3.81818C3.33597 13.8909 2.87351 13.6994 2.53253 13.3584C2.19156 13.0174 2 12.5549 2 12.0727C2 11.5905 2.19156 11.1281 2.53253 10.7871C2.87351 10.4461 3.33597 10.2545 3.81818 10.2545H3.9C4.2009 10.2475 4.49273 10.1501 4.73754 9.97501C4.98236 9.79991 5.16883 9.55521 5.27273 9.27273C5.39374 8.99853 5.42984 8.69437 5.37637 8.39947C5.3229 8.10456 5.18231 7.83244 4.97273 7.61818L4.91818 7.56364C4.74913 7.39478 4.61503 7.19425 4.52353 6.97353C4.43203 6.7528 4.38493 6.51621 4.38493 6.27727C4.38493 6.03834 4.43203 5.80174 4.52353 5.58102C4.61503 5.36029 4.74913 5.15977 4.91818 4.99091C5.08704 4.82186 5.28757 4.68775 5.50829 4.59626C5.72901 4.50476 5.96561 4.45766 6.20455 4.45766C6.44348 4.45766 6.68008 4.50476 6.9008 4.59626C7.12152 4.68775 7.32205 4.82186 7.49091 4.99091L7.54545 5.04545C7.75971 5.25503 8.03183 5.39562 8.32674 5.4491C8.62164 5.50257 8.9258 5.46647 9.2 5.34545H9.27273C9.54161 5.23022 9.77093 5.03887 9.93245 4.79497C10.094 4.55107 10.1807 4.26526 10.1818 3.97273V3.81818C10.1818 3.33597 10.3734 2.87351 10.7144 2.53253C11.0553 2.19156 11.5178 2 12 2C12.4822 2 12.9447 2.19156 13.2856 2.53253C13.6266 2.87351 13.8182 3.33597 13.8182 3.81818V3.9C13.8193 4.19253 13.906 4.47834 14.0676 4.72224C14.2291 4.96614 14.4584 5.15749 14.7273 5.27273C15.0015 5.39374 15.3056 5.42984 15.6005 5.37637C15.8954 5.3229 16.1676 5.18231 16.3818 4.97273L16.4364 4.91818C16.6052 4.74913 16.8057 4.61503 17.0265 4.52353C17.2472 4.43203 17.4838 4.38493 17.7227 4.38493C17.9617 4.38493 18.1983 4.43203 18.419 4.52353C18.6397 4.61503 18.8402 4.74913 19.0091 4.91818C19.1781 5.08704 19.3122 5.28757 19.4037 5.50829C19.4952 5.72901 19.5423 5.96561 19.5423 6.20455C19.5423 6.44348 19.4952 6.68008 19.4037 6.9008C19.3122 7.12152 19.1781 7.32205 19.0091 7.49091L18.9545 7.54545C18.745 7.75971 18.6044 8.03183 18.5509 8.32674C18.4974 8.62164 18.5335 8.9258 18.6545 9.2V9.27273C18.7698 9.54161 18.9611 9.77093 19.205 9.93245C19.4489 10.094 19.7347 10.1807 20.0273 10.1818H20.1818C20.664 10.1818 21.1265 10.3734 21.4675 10.7144C21.8084 11.0553 22 11.5178 22 12C22 12.4822 21.8084 12.9447 21.4675 13.2856C21.1265 13.6266 20.664 13.8182 20.1818 13.8182H20.1C19.8075 13.8193 19.5217 13.906 19.2778 14.0676C19.0339 14.2291 18.8425 14.4584 18.7273 14.7273Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span class="menu-label">AI配置</span>
          </el-menu-item>
          <el-menu-item index="/projects" class="menu-item">
            <svg class="menu-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M13 7L11.8845 4.76892C11.5634 4.1268 11.4029 3.80573 11.1634 3.57116C10.9516 3.36373 10.6963 3.20597 10.4161 3.10931C10.0992 3 9.74021 3 9.02229 3H5.2C4.0799 3 3.51984 3 3.09202 3.21799C2.71569 3.40973 2.40973 3.71569 2.21799 4.09202C2 4.51984 2 5.0799 2 6.2V7M2 7H17.2C18.8802 7 19.7202 7 20.362 7.32698C20.9265 7.6146 21.3854 8.07354 21.673 8.63803C22 9.27976 22 10.1198 22 11.8V16.2C22 17.8802 22 18.7202 21.673 19.362C21.3854 19.9265 20.9265 20.3854 20.362 20.673C19.7202 21 18.8802 21 17.2 21H6.8C5.11984 21 4.27976 21 3.63803 20.673C3.07354 20.3854 2.6146 19.9265 2.32698 19.362C2 18.7202 2 17.8802 2 16.2V7Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span class="menu-label">项目管理</span>
          </el-menu-item>
          <el-menu-item index="/review" class="menu-item">
            <svg class="menu-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 5H7.2C6.0799 5 5.51984 5 5.09202 5.21799C4.71569 5.40973 4.40973 5.71569 4.21799 6.09202C4 6.51984 4 7.0799 4 8.2V20L8.5 17.5L12 20L15.5 17.5L20 20V8.2C20 7.0799 20 6.51984 19.782 6.09202C19.5903 5.71569 19.2843 5.40973 18.908 5.21799C18.4802 5 17.9201 5 16.8 5H15M9 5C9 6.10457 9.89543 7 11 7H13C14.1046 7 15 6.10457 15 5M9 5C9 3.89543 9.89543 3 11 3H13C14.1046 3 15 3.89543 15 5M12 12H16M12 16H16M8 12H8.01M8 16H8.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span class="menu-label">代码审查</span>
          </el-menu-item>
          <el-menu-item index="/branch-review" class="menu-item">
            <svg class="menu-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M6 3V15M18 9V21M6 15C4.34315 15 3 16.3431 3 18C3 19.6569 4.34315 21 6 21C7.65685 21 9 19.6569 9 18C9 16.3431 7.65685 15 6 15ZM18 9C16.3431 9 15 7.65685 15 6C15 4.34315 16.3431 3 18 3C19.6569 3 21 4.34315 21 6C21 7.65685 19.6569 9 18 9ZM18 9C16.3431 9 15 10.3431 15 12C15 13.6569 16.3431 15 18 15C19.6569 15 21 13.6569 21 12C21 10.3431 19.6569 9 18 9Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span class="menu-label">分支审查</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@400;500;600;700;800&display=swap');

:root {
  /* 橙色温暖色调 */
  --primary-orange: #FF8C42;
  --primary-orange-light: #FFB380;
  --primary-orange-lighter: #FFD4B3;
  --primary-orange-dark: #E67A2E;
  --accent-peach: #FFAA80;
  --accent-coral: #FF6B6B;

  /* 中性色 */
  --bg-cream: #FFF8F0;
  --bg-white: #FFFFFF;
  --bg-light: #FFF5EB;
  --text-dark: #4A3728;
  --text-medium: #8B7355;
  --text-light: #B8A490;
  --border-light: #F0E6D9;
  --shadow-soft: rgba(255, 140, 66, 0.08);
  --shadow-medium: rgba(255, 140, 66, 0.15);

  /* 动画时长 */
  --transition-fast: 0.2s;
  --transition-normal: 0.3s;
  --transition-slow: 0.5s;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  color: var(--text-dark);
  background: var(--bg-cream);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

h1, h2, h3, h4, h5, h6 {
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  color: var(--text-dark);
}

/* 侧边栏样式 */
.sidebar {
  background: linear-gradient(180deg, #FFF8F0 0%, #FFF5EB 100%);
  border-right: 1px solid var(--border-light);
  box-shadow: 2px 0 12px var(--shadow-soft);
  transition: all var(--transition-normal) cubic-bezier(0.4, 0, 0.2, 1);
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 28px 24px;
  border-bottom: 1px solid var(--border-light);
  background: var(--bg-white);
}

.logo-icon {
  width: 32px;
  height: 32px;
  color: var(--primary-orange);
  flex-shrink: 0;
}

.logo-text {
  font-family: 'Poppins', sans-serif;
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary-orange) 0%, var(--accent-coral) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sidebar-menu {
  border: none;
  padding: 16px 12px;
}

.menu-item {
  margin-bottom: 8px;
  border-radius: 12px;
  transition: all var(--transition-normal) cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  cursor: pointer;
}

.menu-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 4px;
  height: 100%;
  background: var(--primary-orange);
  transform: scaleY(0);
  transition: transform var(--transition-normal) cubic-bezier(0.4, 0, 0.2, 1);
}

.menu-item:hover {
  background: var(--bg-white);
  box-shadow: 0 4px 12px var(--shadow-soft);
}

.menu-item.is-active {
  background: linear-gradient(135deg, var(--primary-orange-lighter) 0%, var(--bg-white) 100%);
  box-shadow: 0 4px 16px var(--shadow-medium);
}

.menu-item.is-active::before {
  transform: scaleY(1);
}

.menu-icon {
  width: 20px;
  height: 20px;
  margin-right: 12px;
  flex-shrink: 0;
  transition: transform var(--transition-fast);
}

.menu-item:hover .menu-icon {
  transform: scale(1.1);
}

.menu-label {
  font-weight: 500;
  font-size: 15px;
}

/* 主内容区域 */
.main-content {
  background: var(--bg-cream);
  padding: 32px;
  overflow-y: auto;
}

/* 页面切换动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all var(--transition-normal) cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* Element Plus 组件样式覆盖 */
.el-button {
  border-radius: 10px;
  font-weight: 500;
  transition: all var(--transition-fast) cubic-bezier(0.4, 0, 0.2, 1);
  border: none;
}

.el-button--primary {
  background: linear-gradient(135deg, var(--primary-orange) 0%, var(--primary-orange-dark) 100%);
  box-shadow: 0 4px 12px var(--shadow-medium);
}

.el-button--primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px var(--shadow-medium);
}

.el-button--primary:active {
  transform: translateY(0);
}

.el-card {
  border-radius: 16px;
  border: 1px solid var(--border-light);
  box-shadow: 0 2px 12px var(--shadow-soft);
  transition: all var(--transition-normal) cubic-bezier(0.4, 0, 0.2, 1);
  background: var(--bg-white);
}

.el-card:hover {
  box-shadow: 0 8px 24px var(--shadow-medium);
  transform: translateY(-2px);
}

.el-input__wrapper {
  border-radius: 10px;
  box-shadow: 0 2px 8px var(--shadow-soft);
  transition: all var(--transition-fast);
}

.el-input__wrapper:hover {
  box-shadow: 0 4px 12px var(--shadow-soft);
}

.el-input__wrapper.is-focus {
  box-shadow: 0 0 0 3px var(--primary-orange-lighter);
}

.el-select .el-input__wrapper {
  border-radius: 10px;
}

.el-tag {
  border-radius: 8px;
  border: none;
  font-weight: 500;
}

.el-tag--primary {
  background: var(--primary-orange-lighter);
  color: var(--primary-orange-dark);
}

.el-tag--success {
  background: #D4EDDA;
  color: #155724;
}

.el-tag--warning {
  background: #FFF3CD;
  color: #856404;
}

.el-tag--danger {
  background: #F8D7DA;
  color: #721C24;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-light);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: var(--primary-orange-light);
  border-radius: 4px;
  transition: background var(--transition-fast);
}

::-webkit-scrollbar-thumb:hover {
  background: var(--primary-orange);
}

/* 加载动画 */
@keyframes shimmer {
  0% { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
}

.loading-shimmer {
  animation: shimmer 2s infinite linear;
  background: linear-gradient(90deg, var(--bg-light) 0%, var(--primary-orange-lighter) 50%, var(--bg-light) 100%);
  background-size: 1000px 100%;
}
</style>
