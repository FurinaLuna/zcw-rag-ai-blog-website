<template>
  <button
    :type="type"
    :class="btnClass"
    :disabled="disabled || loading"
    :aria-label="ariaLabel"
    :aria-busy="loading"
    :style="{ height: sizeHeight }"
  >
    <span v-if="loading" class="mr-1.5 inline-block h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent" />
    <slot />
  </button>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    variant?: "primary" | "secondary" | "ghost" | "danger" | "icon";
    size?: "sm" | "md" | "lg" | "icon";
    type?: "button" | "submit" | "reset";
    disabled?: boolean;
    loading?: boolean;
    ariaLabel?: string;
    block?: boolean;
  }>(),
  { variant: "primary", size: "md", type: "submit", disabled: false, loading: false, block: false }
);

const sizeH: Record<string, string> = { sm: "32px", md: "40px", lg: "48px", icon: "36px" };
const sizeT: Record<string, string> = { sm: "text-xs", md: "text-sm", lg: "text-sm", icon: "text-sm" };

const sizeHeight = computed(() => sizeH[props.size]);
const sizePad = computed(() => ""); // unused for now

const base = computed(() => [
  "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent",
  sizeT[props.size],
  props.block ? "w-full" : "",
]);

const variantMap: Record<string, string> = {
  primary: "bg-accent text-white hover:opacity-90 active:opacity-80",
  secondary: "border border-border-default bg-white text-text-primary hover:border-accent hover:text-accent active:bg-gray-50",
  ghost: "text-text-secondary hover:bg-gray-100 hover:text-text-primary active:bg-gray-200",
  danger: "text-red-600 hover:bg-red-50 active:bg-red-100 border border-red-200",
  icon: "text-text-tertiary hover:text-text-primary hover:bg-gray-100 rounded-md",
};

const btnClass = computed(() => [
  ...base.value,
  variantMap[props.variant],
  props.disabled || props.loading ? "opacity-50 cursor-not-allowed pointer-events-none" : "cursor-pointer",
  { "w-9": props.size === "icon" },
]);
</script>
