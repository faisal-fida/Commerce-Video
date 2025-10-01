import { Product } from "@/lib/types";
import ProductCard from "./ProductCard";

interface ProductDisplayProps {
    products: Product[];
    hasSearched: boolean;
}

export default function ProductDisplay({
    products,
    hasSearched,
}: ProductDisplayProps) {
    const groupedProducts = products.reduce((acc, product) => {
        const key = product.object_type;
        if (!acc[key]) {
            acc[key] = [];
        }
        acc[key].push(product);
        return acc;
    }, {} as Record<string, Product[]>);

    if (products.length === 0) {
        const message = hasSearched
            ? "No products found at this timestamp."
            : "Pause the video to see detected products.";
        return <div className="text-center py-8 text-gray-500">{message}</div>;
    }

    return (
        <div>
            <h2 className="text-2xl font-bold mb-4 text-white">Detected Products</h2>
            {Object.entries(groupedProducts).map(([type, products]) => (
                <div key={type} className="mb-8">
                    <h3 className="text-xl font-semibold capitalize mb-4 text-gray-300">
                        {type}
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {products.map((product, index) => (
                            <ProductCard key={`${product.direct_url}-${index}`} product={product} />
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
}
