module access_control::gate {
    use std::signer;
    use aptos_framework::coin;

    struct AccessControl has key {
        use_agent: bool,
    }

    public entry fun set_access<UserCoin>(
        user: &signer,
        required_balance: u64
    ) acquires AccessControl {
        let user_addr = signer::address_of(user);
        let balance = coin::balance<UserCoin>(user_addr);
        assert!(balance >= required_balance, 1);

        if (!exists<AccessControl>(user_addr)) {
            move_to(user, AccessControl { use_agent: true });
        } else {
            let access = borrow_global_mut<AccessControl>(user_addr);
            access.use_agent = true;
        }
    }

    public fun check_access(account: address): bool acquires AccessControl {
        if (exists<AccessControl>(account)) {
            let access = borrow_global<AccessControl>(account);
            access.use_agent
        } else {
            false
        }
    }

    // ------------ NEW VIEW FUNCTION ------------
    /// A purely read-only function you can call via /view
    public fun check_access_view(account: address): bool acquires AccessControl {
        check_access(account)
    }
}
