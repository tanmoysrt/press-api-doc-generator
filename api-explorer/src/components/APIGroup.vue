<template>
    <div>
        <p class="text-base font-medium">{{ group }}</p>
        <div class="flex flex-col gap-1.5 mt-1">
            <API v-for="api in apis" :key="api.path" :api="api" />
        </div>
    </div>
</template>
<script setup>
import API from "./API.vue";

const props = defineProps({
    group: {
        type: String,
        required: true,
    },
    apis: {
        type: Array,
        required: true,
    },
});
</script>
