package com.shop.orders;
//package com.business.billing;
public class OrderProcessor {
    private double totalPrice;
    private String orderStatus;
    private List<String> items;

    public void addItem(String item, double price) {
        this.items.add(item);
        this.totalPrice += price;
    }

    public void updateStatus(String newStatus) {
        this.orderStatus = newStatus;
    }

    public double calculateTax() {
        return this.totalPrice * 0.20;
    }

    public String getOrderSummary() {
        return "Order status: " + orderStatus + " | Total: " + totalPrice;
    }
}
