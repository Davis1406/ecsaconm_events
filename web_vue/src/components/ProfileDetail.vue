<template>
    <div class="flex flex-row p-3 space-x-3 py-1 rounded-md text-sm bg-st-tropaz-100">
        <div class="w-3/12 text-st-tropaz-900 font-bold">{{ label }}</div>
        <div class="flex-1">: {{ value }}</div>
    </div>
</template>

<script>
export default {
    props: {
        label: String,
        value: String,
    },
};
</script>
