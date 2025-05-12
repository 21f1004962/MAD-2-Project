<template>
  <div>
    <NavbarVue>
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
      <div class="container mt-4">
        <h2 class="text-center">YOUR CART</h2>
        <br />

        <table class="table table-striped">
          <thead>
            <tr>
              <th>Sno</th>
              <th>Product</th>
              <th>Category</th>
              <th>Quantity</th>
              <th>rate/unit</th>
              <th>unit</th>
              <th>total price</th>
              <th></th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(product, index) in products" :key="index">
              <td>{{ product.sno }}</td>
              <td>{{ product.name }}</td>
              <td>{{ product.category }}</td>
              <td>{{ product.quantity }}</td>
              <td>{{ product.rate }}</td>
              <td>{{ product.rateunits }}</td>
              <td>{{ product.cost }}</td>
              <td>
                <button
                  class="btn btn-info"
                  data-bs-toggle="modal"
                  :data-bs-target="'#m1_' + productNameToId(product.name)"
                  data-bs-backdrop="static"
                  data-bs-keyboard="false"
                >
                  Review
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
                        >
                          <span aria-hidden="true">&times;</span>
                        </button>
                      </div>
                      <div class="modal-body">
                        <div class="container">
                          <form
                            class="form-horizontal"
                            @submit.prevent="
                              handleReviewEdit(
                                product.productid,
                                product.cartid
                              )
                            "
                          >
                            <h5 style="font-weight: normal">
                              Price: {{ product.rate }}
                            </h5>
                            <h5 style="font-weight: normal">
                              Availability: {{ product.availableQuantity }}
                            </h5>
                            <h5 style="font-weight: normal">
                              Quantity in cart: {{ product.quantity }}
                            </h5>
                            <input
                              type="hidden"
                              :value="product.productid"
                              name="productid"
                            />
                            <input
                              type="hidden"
                              :value="product.cartid"
                              name="cartid"
                            />
                            <div class="form-group row">
                              <div class="col-sm-10">
                                <input
                                  v-model="productReviewEditForm.quantity"
                                  type="number"
                                  class="form-control"
                                  placeholder="Change quantity, if you wish to."
                                />
                                <div
                                  v-if="productReviewEditForm.errors.quantity"
                                  class="text-danger"
                                >
                                  {{ productReviewEditForm.errors.quantity[0] }}
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
                                Edit
                              </button>
                            </div>
                          </form>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </td>
              <td>
                <button
                  @click="handleDelete(product.productid, product.cartid)"
                  class="btn btn-danger"
                >
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <br />
        <br />
        <div style="width: 100%; text-align: right">
          <h4 style="font-weight: bold">Grand total : Rs. {{ total }}</h4>
          <button
            @click="handleCheckout"
            class="btn btn-primary"
            :disabled="products.length === 0"
          >
            Checkout
          </button>
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
  name: "UserCartView",
  components: {
    NavbarVue,
    MessagesVue,
    LogoutButtonVue,
  },
  data() {
    return {
      productReviewEditForm: {
        quantity: 0,
        errors: {},
      },
      messages: [],
      products: [],
      total: 0,
    };
  },
  beforeCreate() {
    const jwtToken = localStorage.getItem("jwtToken");
    let apiUrl = "http://127.0.0.1:5000/userGetCart";

    axios
      .get(apiUrl, {
        headers: { "x-access-token": jwtToken },
      })
      .then((response) => {
        this.products = response.data;
        this.total = this.products.reduce(
          (sum, product) => sum + product.cost,
          0
        );
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
    productNameToId(name) {
      return name.replace(/\s/g, "").replace("(", "").replace(")", "");
    },
    handleReviewEdit(productId, cartId) {
      const jwtToken = localStorage.getItem("jwtToken");
      const apiUrl = `http://127.0.0.1:5000/userReviewEditProduct`;

      const formData = new FormData();
      formData.append("productid", productId);
      formData.append("cartid", cartId);
      formData.append("quantity", this.productReviewEditForm.quantity);

      axios
        .put(apiUrl, formData, {
          headers: {
            "x-access-token": jwtToken,
            "Content-Type": "multipart/form-data",
          },
        })
        .then((response) => {
          this.showMessage({
            type: "success",
            text: response.data,
          });
          setTimeout(() => {
            window.location.reload();
          }, 2000);
        })
        .catch((error) => {
          this.showMessage({
            type: "error",
            text: error.response.data,
          });
        });
    },
    handleDelete(productId, cartId) {
      const jwtToken = localStorage.getItem("jwtToken");
      const apiUrl = `http://127.0.0.1:5000/userDeleteProduct`;

      const formData = new FormData();
      formData.append("productid", productId);
      formData.append("cartid", cartId);

      axios
        .delete(apiUrl, {
          headers: {
            "x-access-token": jwtToken,
          },
          data: formData,
        })
        .then((response) => {
          this.showMessage({
            type: "success",
            text: response.data,
          });

          setTimeout(() => {
            window.location.reload();
          }, 2000);
        })
        .catch((error) => {
          this.showMessage({
            type: "error",
            text: error.response.data,
          });
        });
    },

    handleCheckout() {
      const jwtToken = localStorage.getItem("jwtToken");
      const apiUrl = "http://127.0.0.1:5000/checkout";

      axios
        .get(apiUrl, {
          headers: { "x-access-token": jwtToken },
        })
        .then((response) => {
          this.showMessage({
            type: "success",
            text: response.data,
          });

          setTimeout(() => {
            window.location.reload();
          }, 2000);
        })
        .catch((error) => {
          this.showMessage({
            type: "error",
            text: error.response.data,
          });
        });
    },
  },
};
</script>

<style scoped></style>
