import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentRoute = ref('')
const separator = ref('/')

watch(() => route.path, (newPath) => {
  currentRoute.value = newPath
}, { immediate: true })

defineExpose({
  currentRoute,
  separator
}) 