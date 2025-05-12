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
    <div class="main-content">
      <div class="container mt-4">
        <div v-if="Object.keys(order_dict).length > 0">
          <div
            v-for="(order, orderId) in order_dict"
            :key="orderId"
            class="card mb-4"
          >
            <div class="card-header">
              <h5>Order ID: {{ orderId }}</h5>
            </div>
            <div class="card-body">
              <table class="table">
                <thead>
                  <tr>
                    <th>Product Name</th>
                    <th>Quantity Sold</th>
                    <th>Cost per unit</th>
                    <th>Units</th>
                    <th>Total cost</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="product in order" :key="product.productid">
                    <td>{{ product.name }}</td>
                    <td>{{ product.quantitySold }}</td>
                    <td>{{ product.rate }}</td>
                    <td>{{ product.rateunits }}</td>
                    <td>{{ product.cost }}</td>
                  </tr>
                </tbody>
              </table>
              <h5>Total order cost: {{ total_cost[orderId] }}</h5>
            </div>
          </div>
        </div>
        <div v-else>
          <h1 class="text-danger">No orders to be displayed!</h1>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import LogoutButtonVue from "../components/LogoutButton.vue";
import NavbarVue from "../components/Navbar.vue";
import axios from "axios";

export default {
  name: "UserOrdersView",
  components: {
    NavbarVue,
    LogoutButtonVue,
  },
  data() {
    return {
      order_dict: {},
      total_cost: {},
    };
  },
  beforeCreate() {
    const jwtToken = localStorage.getItem("jwtToken");

    axios
      .get('http://127.0.0.1:5000/userOrderHistory', {
        headers: { "x-access-token": jwtToken },
      })
      .then((response) => {
        this.order_dict = response.data.order_dict;
        this.total_cost = response.data.total_cost;
      })
      .catch((error) => {
        console.error('Error fetching orders:', error);
      });
},

};
</script>

<style scoped></style>
