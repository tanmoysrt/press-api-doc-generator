<template>
    <div class="py-1cursor-pointer">
        <div class="flex justify-between items-center">
            <p class="text-sm pl-1">{{ api.path }}</p>
            <button
                class="border border-gray-400 px-2 py-0.5 rounded-md text-sm"
            >
                View Docs
            </button>
        </div>
    </div>
</template>
<script setup>
const props = defineProps({
    api: {
        type: Object,
        required: true,
    },
});
</script>
