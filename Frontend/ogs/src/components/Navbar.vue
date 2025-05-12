<template>
    <nav class="navbar">
        <div class="navbar-left">
            <img src="../../public/icon.png" alt="Icon" class="icon">
            <router-link to="/">GROCER EXPRESS</router-link>
        </div>
        <div class="navbar-right">
            <slot></slot>
        </div>
    </nav>
</template>

<script>
    export default {
        name : "NavbarVue",
    }
</script>

<style scoped>
.navbar {
    background-color: darkgrey;
    display: flex;
    align-items: center;
    padding: 10px 20px;
}

.navbar-left {
  display: flex;
  align-items: center;
  flex: 1;
}

.icon {
  width: 30px;
  height: 30px;
  margin-right: 10px;
}

.brand:hover {
  text-decoration: underline;
}

.navbar-right {
  display: flex;
  text-align: center;
}
</style>