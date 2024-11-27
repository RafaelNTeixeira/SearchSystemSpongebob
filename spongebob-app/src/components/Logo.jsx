import logo from "@/app/assets/logo.png"
import Image from "next/image"


export function Logo() {
    return (
        <div className="flex items-center justify-center my-6">
            <Image src={logo} alt="SpongeBob Logo" width={200} height={200} />
        </div>
    )
}





