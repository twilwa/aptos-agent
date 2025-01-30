module access::simple_storage {
    use std::signer;

    struct SimpleStorage has key {
        value: u64,
    }

    public entry fun store_value(user: &signer, value: u64) acquires SimpleStorage {
        let user_addr = signer::address_of(user);

        if (!exists<SimpleStorage>(user_addr)) {
            move_to(user, SimpleStorage { value });
        } else {
            let storage = borrow_global_mut<SimpleStorage>(user_addr);
            storage.value = value;
        }
    }

    public fun get_value(account: address): u64 acquires SimpleStorage {
        if (exists<SimpleStorage>(account)) {
            let storage = borrow_global<SimpleStorage>(account);
            storage.value
        } else {
            0
        }
    }
}