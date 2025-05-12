<template>
  <div>
    <NavbarVue>
      <div class="search-container">
        <select v-model="searchType" class="search-dropdown">
          <option value="category">Category</option>
          <option value="products" selected="selected">Product</option>
        </select>
        <input
          v-model="searchQuery"
          type="text"
          class="search-bar"
          placeholder="Search..."
        />
        <button @click="search" class="search-button">Search</button>
      </div>
      <a
        href="/userHome"
        class="nav-item nav-link"
        style="display: inline; color: black"
        >Home</a
      >
      <a
        href="/userCart"
        class="nav-item nav-link"
        style="display: inline; color: black"
        >Cart</a
      >
      <a
        href="/userOrders"
        class="nav-item nav-link"
        style="display: inline; color: black"
        >Orders</a
      >
      <LogoutButtonVue style="max-height: 40px" />
    </NavbarVue>
    <MessagesVue :messages="messages" />
    <div class="main-content">
      <div v-if="!catProds">
        <h1 class="text-danger">No Products to be displayed!</h1>
      </div>
      <div v-else>
        <div v-for="(products, category) in catProds" :key="category">
          <div class="container mt-5 category-container">
            <h2 class="text-center">{{ category }}</h2>
            <div class="row mx-auto my-auto justify-content-center">
              <div
                v-for="product in products"
                :key="product.productid"
                class="col-md-3 d-inline-block"
              >
                <div class="card">
                  <div class="card-header">
                    {{ product.name }}
                  </div>
                  <div class="card-body">
                    <h6 class="card-title">
                      Price: {{ product.rate }} Rs/{{ product.rateunits }}
                    </h6>
                    <div v-if="product.quantity > 0">
                      <div>
                        <button
                          class="btn btn-dark"
                          data-bs-toggle="modal"
                          :data-bs-target="
                            '#m1_' + productNameToId(product.name)
                          "
                          data-bs-backdrop="static"
                          data-bs-keyboard="false"
                        >
                          <i class="fas fa-shopping-cart"></i> Buy
                        </button>
                        <div
                          :id="'m1_' + productNameToId(product.name)"
                          class="modal fade"
                          tabindex="-1"
                          role="dialog"
                          aria-labelledby="modalLabel1"
                          aria-hidden="true"
                        >
                          <div class="modal-dialog" role="document">
                            <div class="modal-content">
                              <div class="modal-header">
                                <h5 class="modal-title" id="modalLabel1">
                                  {{ product.name }}
                                </h5>
                                <button
                                  type="button"
                                  class="close"
                                  data-bs-dismiss="modal"
                                  aria-label="Close"
                                  @click="
                                    () => {
                                      buyQuantity = 1;
                                      buyError = null;
                                    }
                                  "
                                >
                                  <span aria-hidden="true">&times;</span>
                                </button>
                              </div>
                              <div class="modal-body">
                                <div class="container">
                                  <form
                                    class="form-horizontal"
                                    @submit.prevent="
                                      handleBuy(product.productid, product)
                                    "
                                  >
                                    <input
                                      type="hidden"
                                      :value="product.productid"
                                      name="productid"
                                    />
                                    <h5 style="font-weight: normal">
                                      Price: {{ product.rate }} Rs/{{
                                        product.rateunits
                                      }}
                                    </h5>
                                    <h5 style="font-weight: normal">
                                      Availability: {{ product.quantity }}
                                      {{ product.rateunits }}s
                                    </h5>
                                    <div class="form-group row">
                                      <div class="col-sm-10">
                                        <input
                                          v-model="buyQuantity"
                                          type="number"
                                          class="form-control"
                                          placeholder="Enter quantity"
                                          required
                                        />
                                        <div
                                          v-if="buyError"
                                          class="text-danger"
                                        >
                                          {{ buyError }}
                                        </div>
                                      </div>
                                    </div>
                                    <br />
                                    <div class="form-group mt-2">
                                      <button
                                        type="submit"
                                        class="btn btn-success"
                                        data-bs-dismiss="modal"
                                      >
                                        Buy
                                      </button>
                                    </div>
                                  </form>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div v-else>
                      <h5 class="text-danger">Out of Stock!</h5>
                    </div>
                  </div>
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
  name: "UserHomeView",
  components: {
    NavbarVue,
    MessagesVue,
    LogoutButtonVue,
  },
  data() {
    return {
      buyQuantity: 1,
      buyError: null,
      catProds: [],
      searchQuery: "",
      searchType: "",
      messages: [],
    };
  },
  beforeCreate() {
    const jwtToken = localStorage.getItem("jwtToken");
    this.searchType = this.$route.query.searchType;
    this.searchQuery = this.$route.query.searchQuery;
    let apiUrl = "http://127.0.0.1:5000/userGetProducts";
    if (this.searchType && this.searchQuery) {
      apiUrl += `?searchType=${this.searchType}&searchKey=${this.searchQuery}`;
    }

    axios
      .get(apiUrl, {
        headers: { "x-access-token": jwtToken },
      })
      .then((response) => {
        this.catProds = response.data;
      })
      .catch((error) => {
        console.error("Error fetching products:", error);
      });
  },
  methods: {
    showMessage(message) {
      this.messages.push(message);

      setTimeout(() => {
        this.messages.shift();
      }, 5000);
    },
    search() {
      const currentUrl = window.location.href;
      const parts = currentUrl.split("?");
      const firstPart = parts[0];

      const newUrl = `${firstPart}?searchType=${this.searchType}&searchQuery=${this.searchQuery}`;
      window.location.href = newUrl;
    },
    productNameToId(name) {
      return name.replace(/\s/g, "").replace("(", "").replace(")", "");
    },
    handleBuy(productId, product) {
      if (this.buyQuantity <= 0) {
        this.buyError = "Quantity must be greater than 0";
      } else if (this.buyQuantity > product.quantity) {
        this.buyError = "Not enough stock available";
      } else {
        const jwtToken = localStorage.getItem("jwtToken");

        const formData = new FormData();
        formData.append("productid", productId);
        formData.append("quantity", this.buyQuantity);

        axios
          .post("http://127.0.0.1:5000/userAddProduct", formData, {
            headers: {
              "Content-Type": "multipart/form-data",
              "x-access-token": jwtToken,
            },
          })
          .then((response) => {
            this.showMessage({ text: response.data, type: "success" });
          })
          .catch((error) => {
            this.showMessage({ text: error.response.data, type: "failure" });
          });
        this.buyQuantity = 1;
        this.buyError = null;
      }
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

.category-container {
  background-color: lightgreen;
  padding: 20px;
  margin-top: 20px;
  max-height: 250px; /* Set the container height for one row of cards */
  overflow-y: scroll; /* Add a vertical scrollbar */
  margin-bottom: 40px;
}

.dropdown-menu {
  background-color: #f8f9fa;
  /* Lighter color for dropdown menu */
}

/* Basic styles for the search bar and dropdown */
.search-container {
  display: flex;
  align-items: center;
  width: 600px;
  margin: 20px auto;
  outline: none;
}

.category-dropdown {
  position: relative;
  /* border: 1px solid #ffffff; /* Border to distinguish dropdown from the search bar */
  border-radius: 4px;
  overflow: hidden;
  width: 120px;
  display: inline-flex;
}

.category-dropdown select {
  padding: 8px;
  /*border: 1px solid #ccc; */
  outline: none;
  background-color: #fff;
  /* White background for the dropdown */
  color: #000;
  /* Text color */
  cursor: pointer;
  appearance: auto;
  /* Remove default arrow */
  font-size: 16px;
}

.category-dropdown::after {
  content: "\25BE";
  /* Unicode down arrow character */
  font-size: 10px;
  position: absolute;
  top: 50%;
  right: 8px;
  transform: translateY(-50%);
  pointer-events: auto;
  /* Ensure the arrow doesn't interfere with clicking the dropdown */
}

.search-input {
  padding: 8px;
  width: 350px;
  display: inline-flex;
  border: 1px solid #ccc;
  /*border-left: none; /* Remove the left border of the search input */
  border-radius: 0 4px 4px 0;
}

.search-button {
  padding: 8px;
  background-color: #007bff;
  color: #fff;
  border: 1px solid #007bff;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 5px;
  display: inline-flex;
}
</style>
