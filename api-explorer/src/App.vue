<template>
    <div class="flex justify-center">
        <div class="p-5 flex flex-col space-y-4 max-w-screen-xl">
            <APIGroup
                v-for="(apis, group, _) in ApiSpecs"
                :key="group"
                :group="group"
                :apis="apis"
            />
        </div>
    </div>
</template>
<script setup>
import ApiSpecs from "@/assets/specs.json";
import { onMounted } from "vue";
import APIGroup from "./components/APIGroup.vue";
</script>

<style scoped></style>
