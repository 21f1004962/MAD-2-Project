<template>
  <div>
    <div :style="{ display: showModal ? 'flex' : 'none' }" class="modal">
      <div class="modal-background" @click="closeModal"></div>
      <div class="modal-card">
        <header class="modal-card-head has-background-primary">
          <p class="modal-card-title has-text-white" style="display: inline">
            {{ editingProduct ? "Edit Product" : "Add Product" }}
          </p>
          <button class="delete" style="float: right" @click="closeModal">
            X
          </button>
        </header>
        <section class="modal-card-body">
          <form @submit.prevent="handleSubmit" class="product-form">
            <div class="field">
              <label class="label">Product Name</label>
              <div class="control">
                <input
                  v-model="productName"
                  class="input"
                  type="text"
                  :placeholder="
                    editingProduct ? productNameProp : 'Enter new product name'
                  "
                  required
                />
              </div>
            </div>
            <div class="field">
              <label class="label">Quantity</label>
              <div class="control">
                <input
                  v-model="quantity"
                  class="input"
                  type="number"
                  required
                />
              </div>
            </div>
            <div class="field">
              <label class="label">Rate</label>
              <div class="control">
                <input
                  v-model="rate"
                  class="input"
                  type="number"
                  step="0.5"
                  required
                />
              </div>
            </div>
            <div class="field">
              <label class="label">Rate Units</label>
              <div class="control">
                <select v-model="rateUnits" class="select" required>
                  <option value="kg">kg</option>
                  <option value="litre">litre</option>
                  <option value="dozen">dozen</option>
                  <option value="unit">unit</option>
                </select>
              </div>
            </div>
            <div class="field">
              <div class="control">
                <button type="submit" class="button is-primary">
                  {{ editingProduct ? "Save Changes" : "Add Product" }}
                </button>
              </div>
            </div>
          </form>
        </section>
      </div>
      <button
        class="modal-close is-large"
        aria-label="close"
        @click="closeModal"
      ></button>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  props: {
    showModal: Boolean,
    editingProduct: Boolean,
    productId: Number,
    productNameProp: String,
    quantityProp: Number,
    rateProp: Number,
    rateUnitsProp: String,
    categoryIdProp: Number,
  },
  data() {
    return {
      productName: this.editingProduct ? this.productNameProp : "",
      quantity: this.editingProduct ? this.quantityProp : 0,
      rate: this.editingProduct ? this.rateProp : 0,
      rateUnits: this.editingProduct ? this.rateUnitsProp : "kg",
    };
  },
  methods: {
    closeModal() {
      this.productName = "";
      this.quantity = 0;
      this.rate = 0;
      this.rateUnits = "kg";
      this.categoryId = null;
      this.$emit("close");
    },
    handleSubmit() {
      const jwtToken = localStorage.getItem("jwtToken");
      const formData = new FormData();

      if (this.editingProduct) {
        formData.append("productid", this.productId);
      }

      formData.append("name", this.productName);
      formData.append("quantity", this.quantity);
      formData.append("rate", this.rate);
      formData.append("rateunits", this.rateUnits);

      if (!this.editingProduct) {

        formData.append("categoryid", this.categoryIdProp);
      }

      const axiosConfig = {
        headers: {
          "Content-Type": "multipart/form-data",
          "x-access-token": jwtToken,
        },
      };

      const axiosRequest = this.editingProduct
        ? axios.put(
            "http://127.0.0.1:5000/storeManagerEditProduct",
            formData,
            axiosConfig
          )
        : axios.post(
            "http://127.0.0.1:5000/storeManagerAddProduct",
            formData,
            axiosConfig
          );

      axiosRequest
        .then(() => {
          const messageType = this.editingProduct
            ? "product-updated"
            : "product-added";
          this.$emit(messageType, {
            type: "success",
            text: `Product ${
              this.editingProduct ? "updated" : "added"
            } successfully`,
          });
          this.closeModal();
        })
        .catch((error) => {
          const messageType = this.editingProduct
            ? "product-updated"
            : "product-added";
          this.$emit(messageType, {
            type: "failure",
            text: error.response.data,
          });
          this.closeModal();
        });
    },
  },
};
</script>

<style scoped>
/* Add styles to position the modal */
.modal {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  justify-content: center;
  align-items: center;
}

.modal-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
}

.modal-card {
  position: absolute;
  z-index: 1;
  border: 1px solid #ccc;
  background-color: #fff;
  width: 400px; /* Adjust the width as needed */
}

.has-background-primary {
  background-color: #00d1b2;
}

/* Additional styles for the form container */
.modal-card-body {
  padding: 20px;
}

.product-form {
  padding: 20px;
}

.modal-close {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: transparent;
  border: none;
  cursor: pointer;
}
</style>
