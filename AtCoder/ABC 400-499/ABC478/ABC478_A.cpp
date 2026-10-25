#include <iostream>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, m; cin >> n >> m;
    for (int i = 0; i < n; i++) {
        cout << m/n + (i < m%n) << "\n";
    }
    return 0;
}