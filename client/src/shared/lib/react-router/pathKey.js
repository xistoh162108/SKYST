export const pathKeys = {
    root: "/",
    home: {
        root() {
            return {
                link: pathKeys.root,
                permission: null,
            };
        },
    },
    page404() {
        return pathKeys.root.concat("404/");
    },
};
