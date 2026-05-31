package com.financial.mybank.accounts;

/**
 * Represents a bank account with a single, well-defined responsibility:
 * managing the account balance.
 */
public class BankAccount {

    private double balance;

    public BankAccount(double initialBalance) {
        this.balance = initialBalance;
    }

    public void deposit(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("Amount must be positive");
        }
        balance += amount;
    }

    public void withdraw(double amount) {
        if (amount <= 0 || amount > balance) {
            throw new IllegalArgumentException("Invalid withdrawal amount");
        }
        balance -= amount;
    }

    public boolean hasSufficientFunds(double amount) {
        return balance >= amount;
    }

    public double getBalance() {
        return balance;
    }
}
