<template>
  <div>
    <NavbarVue>
      <div>
        <a
          href="/adminHome"
          class="nav-item nav-link"
          style="display: inline; color: black"
          >Home</a
        >
        <LogoutButtonVue />
      </div>
    </NavbarVue>
    <MessagesVue :messages="messages" />
    <!-- Sign-Up Requests Section -->
      <div class="main-content" style="padding: 20px">
        <h2 style="margin-top: 40px">Sign-Up Requests</h2>
        <div class="scroll-container">
          <div class="card-container">
            <div v-for="request in signUpRequests" :key="request.id" class="card">
              <div class="card-header">
                {{ request.username }}
              </div>
              <div class="card-content">
                <div>Email: {{ request.email }}</div>
              </div>
              <div class="card-footer">
                <div class="action-buttons">
                  <button
                    @click="handleRequest(request.id, 'True', 'SignUp')"
                    class="accept-button"
                  >
                    Accept
                  </button>
                  <button
                    @click="handleRequest(request.id, 'False', 'SignUp')"
                    class="reject-button"
                  >
                    Reject
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

      <!-- Category Requests Slider -->
        <h2 style="margin-top: 40px">Category Requests</h2>
        <div class="scroll-container">
          <div class="card-container">

            <div
              v-for="request in categoryRequests"
              :key="request.id"
              class="card"
            >
              <div class="card-header">
                Requested by: {{ request.requestedBy }}
              </div>
              <div class="card-content">
                <div v-if="request.operation === 'Add'">
                  <div>Category: {{ request.name }} <br />Operation: Add</div>
                </div>
                <div v-else-if="request.operation === 'Edit'">
                  <div>
                    Category: {{ request.name }} <br />Operation: Edit <br />New
                    Name: {{ request.newName }}
                  </div>
                </div>
                <div v-else-if="request.operation === 'Delete'">
                  <div>Category: {{ request.name }} <br />Operation: Delete</div>
                </div>
                <div v-else>
                  <!-- Handle other operations if needed -->
                  <div>Unknown operation</div>
                </div>
                <div class="card-footer">
                  <div class="action-buttons">
                    <button
                      @click="handleRequest(request.id, 'True', 'Category')"
                      class="accept-button"
                    >
                      Accept
                    </button>
                    <button
                      @click="handleRequest(request.id, 'False', 'Category')"
                      class="reject-button"
                    >
                      Reject
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<script>
import LogoutButtonVue from "../components/LogoutButton.vue";
import NavbarVue from "../components/Navbar.vue";
import axios from "axios";
import MessagesVue from "../components/Messages.vue";

export default {
  name: "AdminRequestsView",
  data() {
    return {
      signUpRequests: [],
      categoryRequests: [],
      messages: [],
    };
  },
  components: {
    NavbarVue,
    LogoutButtonVue,
    MessagesVue,
  },
  beforeCreate() {
    const jwtToken = localStorage.getItem("jwtToken");

    axios
      .get("http://127.0.0.1:5000/adminGetSignUpRequests", {
        headers: { "x-access-token": jwtToken },
      })
      .then((response) => {
        this.signUpRequests = response.data.signup_requests;
      })
      .catch((error) => {
        console.error("Error fetching sign up requests:", error);
      });

    axios
      .get("http://127.0.0.1:5000/adminGetCategoryRequests", {
        headers: { "x-access-token": jwtToken },
      })
      .then((response) => {
        this.categoryRequests = response.data.category_requests;
      })
      .catch((error) => {
        console.error("Error fetching category requests:", error);
      });
  },
  methods: {
    handleRequest(requestid, action, endPoint) {
      const jwtToken = localStorage.getItem("jwtToken");
      const apiUrl = `http://127.0.0.1:5000/adminApprove${endPoint}Request`;

      const formData = new FormData();
      formData.append("requestid", requestid);
      formData.append("adminResponse", action);

      axios
        .post(apiUrl, formData, { headers: { "x-access-token": jwtToken } })
        .then((response) => {

          this.showMessage({
            type: "success",
            text: response.data,
          });

          setTimeout(() => {
            window.location.reload(true);
          }, 2000);
        })
        .catch((error) => {
          this.showMessage({
            type: "failure",
            text: error.response.data,
          });

          setTimeout(() => {
            window.location.reload(true);
          }, 2000);
        });
    },
    showMessage(message) {
      this.messages.push(message);

      setTimeout(() => {
        this.messages.shift();
      }, 5000);
    },
  },
};
</script>

<style scoped>
.card {
    margin-bottom: 20px;
    min-height: 170px;
    height: fit-content;
}

/* Styling for the card headers */
.card-header {
  background-color: #f5deb3; /* Light brown background for headers */
  text-align: center;
  font-weight: bold;
}

.card-container {
    background-color: lightgreen;
    padding: 20px;
    margin-top: 20px;
    max-height: 250px; /* Set the container height for one row of cards */
    overflow-y: scroll; /* Add a vertical scrollbar */
    margin-bottom: 40px;
}

.scroll-container {
  overflow-x: auto;
  white-space: nowrap;
  max-width: calc(25% * 4); /* Set maximum width to accommodate 4 cards */
  margin-bottom: 20px; /* Add margin to separate from the content below */
}

.card-footer {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
}

.action-buttons {
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
}

.accept-button,
.reject-button {
  padding: 8px 16px;
  cursor: pointer;
  border: none;
  border-radius: 4px;
  color: #fff;
  font-weight: bold;
}

.accept-button {
  background-color: #4caf50;
}

.reject-button {
  background-color: #f44336;
}
</style>
