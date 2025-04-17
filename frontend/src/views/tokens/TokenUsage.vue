<template>
  <div class="token-usage-container">
    <el-card class="token-summary-card">
      <template #header>
        <div class="card-header">
          <h2>Token 使用统计</h2>
          <div class="header-actions">
            <el-button type="primary" @click="refreshData" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新数据
            </el-button>
            <el-button type="warning" @click="exportData">
              <el-icon><Download /></el-icon>
              导出数据
            </el-button>
            <el-button type="danger" @click="confirmReset">
              <el-icon><Delete /></el-icon>
              重置数据
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>

      <div v-else-if="!usageData" class="no-data">
        <el-empty description="暂无Token使用数据" />
      </div>

      <div v-else class="token-data">
        <div class="total-usage">
          <h3>总体使用情况</h3>
          <el-row :gutter="20">
            <el-col :span="6">
              <el-statistic title="总Token数" :value="usageData.summary.total_usage.total_tokens">
                <template #suffix>
                  <span class="suffix-label">tokens</span>
                </template>
              </el-statistic>
            </el-col>
            <el-col :span="6">
              <el-statistic title="总请求数" :value="usageData.summary.total_usage.requests" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="估算成本" :value="formatCost(usageData.summary.total_usage.estimated_cost)">
                <template #prefix>
                  <span class="prefix-label">$</span>
                </template>
              </el-statistic>
            </el-col>
            <el-col :span="6">
              <el-statistic title="运行时间" :value="formatTime(usageData.summary.uptime_hours)" />
            </el-col>
          </el-row>
        </div>

        <el-divider />

        <div class="usage-charts">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="按模型统计" name="model">
              <div class="chart-container">
                <h4>模型使用情况</h4>
                <div class="model-stats">
                  <el-table :data="modelStats" style="width: 100%">
                    <el-table-column prop="model" label="模型" />
                    <el-table-column prop="total_tokens" label="总Token数" />
                    <el-table-column prop="requests" label="请求数" />
                    <el-table-column prop="estimated_cost" label="估算成本">
                      <template #default="scope">
                        ${{ formatCost(scope.row.estimated_cost) }}
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="按服务统计" name="service">
              <div class="chart-container">
                <h4>服务使用情况</h4>
                <div class="service-stats">
                  <el-table :data="serviceStats" style="width: 100%">
                    <el-table-column prop="service" label="服务" />
                    <el-table-column prop="total_tokens" label="总Token数" />
                    <el-table-column prop="requests" label="请求数" />
                    <el-table-column prop="estimated_cost" label="估算成本">
                      <template #default="scope">
                        ${{ formatCost(scope.row.estimated_cost) }}
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="按日期统计" name="day">
              <div class="chart-container">
                <h4>日期使用情况</h4>
                <div class="day-stats">
                  <el-table :data="dayStats" style="width: 100%">
                    <el-table-column prop="day" label="日期" />
                    <el-table-column prop="total_tokens" label="总Token数" />
                    <el-table-column prop="requests" label="请求数" />
                    <el-table-column prop="estimated_cost" label="估算成本">
                      <template #default="scope">
                        ${{ formatCost(scope.row.estimated_cost) }}
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="最近记录" name="recent">
              <div class="chart-container">
                <h4>最近使用记录</h4>
                <div class="recent-records">
                  <el-button type="primary" @click="loadRecentRecords" :disabled="loadingRecent">
                    加载最近记录
                  </el-button>

                  <div v-if="loadingRecent" class="loading-container">
                    <el-skeleton :rows="5" animated />
                  </div>

                  <div v-else-if="!recentRecords.length" class="no-data">
                    <el-empty description="暂无最近记录" />
                  </div>

                  <el-table v-else :data="recentRecords" style="width: 100%; margin-top: 20px;">
                    <el-table-column prop="timestamp" label="时间" width="180" />
                    <el-table-column prop="model" label="模型" />
                    <el-table-column prop="service" label="服务" />
                    <el-table-column prop="task" label="任务" />
                    <el-table-column prop="total_tokens" label="总Token数" />
                    <el-table-column prop="estimated_cost" label="估算成本">
                      <template #default="scope">
                        ${{ formatCost(scope.row.estimated_cost) }}
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="我的使用摘要" name="user-summary">
              <div class="chart-container">
                <h4>我的Token使用摘要</h4>
                <div v-if="loadingUserData" class="loading-container">
                  <el-skeleton :rows="5" animated />
                </div>

                <div v-else-if="!userSummary" class="no-data">
                  <el-empty description="暂无使用数据" />
                </div>

                <div v-else class="user-summary">
                  <el-row :gutter="20">
                    <el-col :span="8">
                      <el-statistic title="总Token数" :value="userSummary.total_usage.total_tokens">
                        <template #suffix>
                          <span class="suffix-label">tokens</span>
                        </template>
                      </el-statistic>
                    </el-col>
                    <el-col :span="8">
                      <el-statistic title="总请求数" :value="userSummary.total_usage.requests" />
                    </el-col>
                    <el-col :span="8">
                      <el-statistic title="估算成本" :value="formatCost(userSummary.total_usage.estimated_cost)">
                        <template #prefix>
                          <span class="prefix-label">$</span>
                        </template>
                      </el-statistic>
                    </el-col>
                  </el-row>

                  <h5 class="sub-title">按模型统计</h5>
                  <el-table :data="userModelStats" style="width: 100%">
                    <el-table-column prop="model" label="模型" />
                    <el-table-column prop="total_tokens" label="总Token数" />
                    <el-table-column prop="requests" label="请求数" />
                    <el-table-column prop="estimated_cost" label="估算成本">
                      <template #default="scope">
                        ${{ formatCost(scope.row.estimated_cost) }}
                      </template>
                    </el-table-column>
                  </el-table>

                  <h5 class="sub-title">按服务统计</h5>
                  <el-table :data="userServiceStats" style="width: 100%">
                    <el-table-column prop="service" label="服务" />
                    <el-table-column prop="total_tokens" label="总Token数" />
                    <el-table-column prop="requests" label="请求数" />
                    <el-table-column prop="estimated_cost" label="估算成本">
                      <template #default="scope">
                        ${{ formatCost(scope.row.estimated_cost) }}
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="我的使用记录" name="user-records">
              <div class="chart-container">
                <h4>我的Token使用记录</h4>
                <div class="user-records">
                  <el-button type="primary" @click="fetchUserTokenUsage" :disabled="loadingUserData">
                    <el-icon><User /></el-icon>
                    刷新我的记录
                  </el-button>

                  <div v-if="loadingUserData" class="loading-container">
                    <el-skeleton :rows="5" animated />
                  </div>

                  <div v-else-if="!userRecords.length" class="no-data">
                    <el-empty description="暂无使用记录" />
                  </div>

                  <el-table v-else :data="userRecords" style="width: 100%; margin-top: 20px;">
                    <el-table-column prop="timestamp" label="时间" width="180" />
                    <el-table-column prop="model" label="模型" />
                    <el-table-column prop="service" label="服务" />
                    <el-table-column prop="task" label="任务" />
                    <el-table-column prop="total_tokens" label="总Token数" />
                    <el-table-column prop="estimated_cost" label="估算成本">
                      <template #default="scope">
                        ${{ formatCost(scope.row.estimated_cost) }}
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Refresh, Download, Delete, User } from '@element-plus/icons-vue';
import {
  getTokenUsage,
  exportTokenUsage,
  resetTokenUsage,
  getUserTokenUsage,
  getUserTokenUsageSummary
} from '@/api/modules/tokens';
import type {
  TokenUsageResponse,
  UserTokenUsageRecord,
  UserTokenUsageSummary
} from '@/types/tokens';

// 数据和状态
const loading = ref(false);
const loadingRecent = ref(false);
const loadingUserData = ref(false);
const usageData = ref<TokenUsageResponse | null>(null);
const recentRecords = ref<any[]>([]);
const userRecords = ref<UserTokenUsageRecord[]>([]);
const userSummary = ref<UserTokenUsageSummary | null>(null);
const activeTab = ref('model');

// 计算属性
const modelStats = computed(() => {
  if (!usageData.value) return [];

  return Object.entries(usageData.value.summary.by_model).map(([model, stats]) => ({
    model,
    ...stats
  }));
});

const serviceStats = computed(() => {
  if (!usageData.value) return [];

  return Object.entries(usageData.value.summary.by_service).map(([service, stats]) => ({
    service,
    ...stats
  }));
});

const dayStats = computed(() => {
  if (!usageData.value) return [];

  return Object.entries(usageData.value.summary.by_day).map(([day, stats]) => ({
    day,
    ...stats
  }));
});

// 用户模型统计
const userModelStats = computed(() => {
  if (!userSummary.value) return [];

  return Object.entries(userSummary.value.by_model).map(([model, stats]) => ({
    model,
    ...stats
  }));
});

// 用户服务统计
const userServiceStats = computed(() => {
  if (!userSummary.value) return [];

  return Object.entries(userSummary.value.by_service).map(([service, stats]) => ({
    service,
    ...stats
  }));
});

// 格式化成本
const formatCost = (cost: number) => {
  return cost.toFixed(4);
};

// 格式化时间
const formatTime = (hours: number) => {
  const days = Math.floor(hours / 24);
  const remainingHours = Math.floor(hours % 24);
  const minutes = Math.floor((hours * 60) % 60);

  if (days > 0) {
    return `${days}天 ${remainingHours}小时`;
  } else {
    return `${remainingHours}小时 ${minutes}分钟`;
  }
};

// 获取Token使用数据
const fetchData = async () => {
  loading.value = true;
  try {
    const result = await getTokenUsage();
    usageData.value = result;
  } catch (error) {
    console.error('获取Token使用数据失败:', error);
    ElMessage.error('获取Token使用数据失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

// 刷新所有数据
const refreshData = () => {
  fetchData();
  fetchUserTokenUsage();
  fetchUserTokenUsageSummary();
};

// 加载最近记录
const loadRecentRecords = async () => {
  loadingRecent.value = true;
  try {
    const result = await getTokenUsage({ include_recent: true, recent_limit: 20 });
    if (result.recent_records) {
      recentRecords.value = result.recent_records;
    } else {
      recentRecords.value = [];
    }
  } catch (error) {
    console.error('获取最近记录失败:', error);
    ElMessage.error('获取最近记录失败，请稍后重试');
  } finally {
    loadingRecent.value = false;
  }
};

// 导出数据
const exportData = async () => {
  try {
    const result = await exportTokenUsage({ format: 'json' });

    // 创建Blob对象
    const blob = new Blob([result], { type: 'application/json' });

    // 创建下载链接
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `token_usage_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();

    // 清理
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 0);

    ElMessage.success('数据导出成功');
  } catch (error) {
    console.error('导出数据失败:', error);
    ElMessage.error('导出数据失败，请稍后重试');
  }
};

// 确认重置
const confirmReset = () => {
  ElMessageBox.confirm(
    '重置将清除所有Token使用数据，此操作不可恢复，是否继续？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(() => {
      resetData();
    })
    .catch(() => {
      // 取消操作
    });
};

// 重置数据
const resetData = async () => {
  loading.value = true;
  try {
    await resetTokenUsage();
    ElMessage.success('Token使用数据已重置');
    fetchData();
  } catch (error) {
    console.error('重置数据失败:', error);
    ElMessage.error('重置数据失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

// 获取用户Token使用记录
const fetchUserTokenUsage = async () => {
  loadingUserData.value = true;
  try {
    const records = await getUserTokenUsage({ limit: 20 });
    userRecords.value = records;
  } catch (error) {
    console.error('获取用户Token使用记录失败:', error);
    ElMessage.error('获取用户Token使用记录失败，请稍后重试');
  } finally {
    loadingUserData.value = false;
  }
};

// 获取用户Token使用摘要
const fetchUserTokenUsageSummary = async () => {
  loadingUserData.value = true;
  try {
    const summary = await getUserTokenUsageSummary();
    userSummary.value = summary;
  } catch (error) {
    console.error('获取用户Token使用摘要失败:', error);
    ElMessage.error('获取用户Token使用摘要失败，请稍后重试');
  } finally {
    loadingUserData.value = false;
  }
};

// 页面加载时获取数据
onMounted(() => {
  fetchData();
  fetchUserTokenUsage();
  fetchUserTokenUsageSummary();
});
</script>

<style scoped>
.token-usage-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.loading-container {
  padding: 20px 0;
}

.no-data {
  padding: 40px 0;
  text-align: center;
}

.total-usage {
  margin-bottom: 30px;
}

.total-usage h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  color: #303133;
}

.suffix-label, .prefix-label {
  font-size: 12px;
  color: #909399;
  margin: 0 4px;
}

.usage-charts {
  margin-top: 20px;
}

.chart-container {
  margin-top: 20px;
}

.chart-container h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #303133;
}

.model-stats, .service-stats, .day-stats, .recent-records, .user-records, .user-summary {
  margin-top: 20px;
}

.sub-title {
  margin: 30px 0 15px 0;
  font-size: 16px;
  color: #303133;
  border-left: 3px solid #409eff;
  padding-left: 10px;
}

@media (max-width: 768px) {
  .header-actions {
    flex-direction: column;
  }
}
</style>
