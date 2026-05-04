<template>
  <div ref="chartRef" class="h-[320px] w-full" />
</template>

<script setup lang="ts">
import * as echarts from "echarts";

const props = defineProps<{
  data: Array<{ date: string; pv: number }>;
}>();

const chartRef = ref<HTMLElement | null>(null);
let chart: echarts.ECharts | null = null;

function render() {
  if (!chartRef.value) return;
  if (!chart) {
    chart = echarts.init(chartRef.value);
  }

  chart.setOption({
    tooltip: { trigger: "axis" },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: {
      type: "category",
      data: props.data.map((d) => d.date.slice(5)),
      axisLine: { lineStyle: { color: "#E4E0D8" } },
      axisLabel: { color: "#9CA3AF", fontSize: 12 },
    },
    yAxis: {
      type: "value",
      splitLine: { lineStyle: { color: "#F3F4F6" } },
      axisLabel: { color: "#9CA3AF", fontSize: 12 },
    },
    series: [
      {
        name: "PV",
        type: "line",
        data: props.data.map((d) => d.pv),
        smooth: true,
        symbol: "circle",
        symbolSize: 6,
        lineStyle: { color: "#0F766E", width: 2 },
        itemStyle: { color: "#0F766E" },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(15, 118, 110, 0.15)" },
            { offset: 1, color: "rgba(15, 118, 110, 0.01)" },
          ]),
        },
      },
    ],
  });
}

watch(
  () => props.data,
  () => nextTick(render),
);

onMounted(() => {
  nextTick(render);
  window.addEventListener("resize", () => chart?.resize());
});

onUnmounted(() => {
  chart?.dispose();
  window.removeEventListener("resize", () => chart?.resize());
});
</script>
