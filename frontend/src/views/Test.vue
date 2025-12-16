<template>
    <div class="home">
        <img class="vite-logo" src="/icons/vite.svg" alt="Vite Logo" />
        <h1>Pagina Test</h1>
        <router-link to="/">Torna a Home</router-link>
    </div>
</template>

<script setup>
</script>

<style scoped>
.home {
    text-align: center;
    margin-top: 50px;
}

.vite-logo {
    height: 6em;
    padding: 1.5em;
    will-change: filter;
    transition: filter 300ms;
}

.vite-logo:hover {
    filter: drop-shadow(0 0 2em #646cffaa);
}
</style>
