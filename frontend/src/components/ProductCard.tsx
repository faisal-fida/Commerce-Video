import { Product } from "@/lib/types";

interface ProductCardProps {
    product: Product;
}

export default function ProductCard({ product }: ProductCardProps) {
    return (
        <div className="bg-gray-800 rounded-lg overflow-hidden shadow-lg">
            <img
                className="w-full h-48 object-cover"
                src={product.image_url}
                alt={product.title}
            />
            <div className="p-4">
                <h3 className="text-lg font-semibold text-white">{product.title}</h3>
                <p
                    className={`text-sm ${product.stock === "In Stock" ? "text-green-400" : "text-red-400"
                        }`}
                >
                    {product.stock}
                </p>
                <a
                    href={product.direct_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-4 inline-block text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:ring-blue-800 font-medium rounded-lg text-sm px-4 py-2"
                >
                    View Product
                </a>
            </div>
        </div>
    );
}
