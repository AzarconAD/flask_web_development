from fusion_tree import FusionTree

class Restaurant:
    def __init__(self):
        # 3 tables each for 2, 4, and 8 seats
        self.tables = {
            2: FusionTree(),
            4: FusionTree(),
            8: FusionTree()
        }

        # Pre-fill with available table IDs
        for size in self.tables:
            for i in range(1, 4):
                table_id = int(f"{size}{i}")
                self.tables[size].insert(table_id)

        self.queue = []  # waiting customers

    def walk_in(self, customer_name, party_size):
        """Customer arrives for dining"""
        tree = self.tables.get(party_size)
        if tree and not tree.is_empty():
            table_id = tree.get_min()
            tree.delete(table_id)
            return f"Assigned {table_id} to {customer_name}"
        else:
            self.queue.append((customer_name, party_size))
            return f"No table available for {customer_name}, added to queue"

    def finish_meal(self, table_size, table_id):
        """Free a table and assign next in queue if possible"""
        # Re-insert the freed table
        self.tables[table_size].insert(table_id)

        # Check queue
        for i, (name, size) in enumerate(self.queue):
            if size == table_size:
                assigned_table = self.tables[table_size].get_min()
                self.tables[table_size].delete(assigned_table)
                self.queue.pop(i)
                return f"Table {assigned_table} Has Finished their Meal -> Reassigned to {name}"
        return f"Table {table_id} is now free"

    def cancel_customer(self, customer_name):
        """Cancel reservation from queue"""
        for i, (name, size) in enumerate(self.queue):
            if name == customer_name:
                self.queue.pop(i)
                return f"{customer_name}'s request cancelled"
        return f"{customer_name} not found in queue"

    def status(self):
        return {
            "available_tables": {
                size: tree.get_all_keys() for size, tree in self.tables.items()
            },
            "queue": self.queue
        }

