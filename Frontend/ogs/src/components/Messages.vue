<template>
  <div v-if="messages?.length" class="message-container">
    <div v-for="(message, index) in messages" :key="index" :class="getMessageClass(message.type)">
      {{ message.text }}
    </div>
  </div>
</template>

<script>
export default {
  name : "MessagesVue",
  props: {
    messages: Array,
  },
  methods: {
    getMessageClass(type) {
      switch (type) {
        case 'success':
          return 'message success';
        case 'failure':
          return 'message failure';
        case 'information':
          return 'message information';
        default:
          return 'message';
      }
    },
  },
};
</script>

<style scoped>
.message-container {
  top: 0;
  left: 0;
  width: 100%;
  padding: 10px;
  text-align: center;
  z-index: 1000;
}

.message {
  margin-bottom: 10px;
}

.success {
  background-color: #d4edda;
  color: #155724;
}

.failure {
  background-color: #f8d7da;
  color: #721c24;
}

.information {
  background-color: #d1ecf1;
  color: #0c5460;
}
</style>
