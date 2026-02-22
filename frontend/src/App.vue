<template>
  <el-container style="height: 100vh">
    <el-aside width="200px" style="background:#001529">
      <div style="color:#fff;font-size:16px;padding:20px 16px;font-weight:bold">练习册数字化</div>
      <el-menu router background-color="#001529" text-color="#ccc" active-text-color="#fff" :default-active="$route.path">
        <el-menu-item index="/exams"><el-icon><Document /></el-icon>练习册管理</el-menu-item>
        <el-menu-item index="/sessions"><el-icon><EditPen /></el-icon>答题记录</el-menu-item>
        <el-menu-item index="/settings"><el-icon><Setting /></el-icon>AI 设置</el-menu-item>
      </el-menu>
    </el-aside>
    <el-main style="background:#f0f2f5;padding:24px">
      <router-view />
    </el-main>
  </el-container>
</template>
