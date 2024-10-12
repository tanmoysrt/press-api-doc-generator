<template>
    <div class="py-1cursor-pointer">
        <div class="flex justify-between items-center">
            <p class="text-sm pl-1">{{ api.path }}</p>
            <button class="border border-gray-400 px-2 py-0.5 rounded-md text-sm" @click="toggleVisibility">
                View Docs
            </button>
        </div>
        <div v-if="isVisible" class="mt-1">
            <MarkdownRenderer :source="api.description" :is-small-text="true" v-if="api.description" />
            <a :href="api.code_reference" target="_blank" class="text-sm text-blue-500">View Code
                Reference</a>

            <table class="table-auto w-full">
                <thead>
                    <tr>
                        <th class="text-left">Parameter</th>
                        <th class="text-left">Type</th>
                        <th class="text-left">Default</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="details, key in api.parameters" :key="arg">
                        <td class="text-left">{{ key }}</td>
                        <td class="text-left">{{ details.type }}</td>
                        <td class="text-left">{{ details.default }}</td>
                    </tr>
                </tbody>
            </table>

        </div>
    </div>
</template>
<script setup>
import { ref } from 'vue';
import MarkdownRenderer from './MarkdownRenderer.vue';

const props = defineProps({
    api: {
        type: Object,
        required: true,
    },
});

const isVisible = ref(false);

function toggleVisibility() {
    isVisible.value = !isVisible.value;
}
</script>
